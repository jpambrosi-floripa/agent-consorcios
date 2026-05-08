#!/usr/bin/env python3

import os
from datetime import datetime
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from src.session_manager import SessionManager
from src.profile_system import ProfileSystem
from src.objection_bank import ObjectionBank
from src.objection_selector import ObjectionSelector
from src.claude_agent import ClaudeAgent
from src.evaluator import Evaluator
from src.report_generator import ReportGenerator
from src.models import Message, ObjectionUsage

console = Console()
app = typer.Typer()


def get_managers(require_agent=False):
    """Initialize all managers needed for the app"""
    session_mgr = SessionManager(sessions_dir="sessions")
    profile_sys = ProfileSystem(profiles_dir="profiles")
    objection_bank = ObjectionBank(filepath="objections.json")
    objection_selector = ObjectionSelector(objection_bank, profile_sys)
    evaluator = Evaluator()
    report_gen = ReportGenerator()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    agent = None
    if require_agent:
        if not api_key:
            console.print("[red]Error: ANTHROPIC_API_KEY not set in .env[/red]")
            raise typer.Exit(code=1)
        agent = ClaudeAgent(api_key=api_key)
    elif api_key:
        agent = ClaudeAgent(api_key=api_key)

    return {
        "session_mgr": session_mgr,
        "profile_sys": profile_sys,
        "objection_bank": objection_bank,
        "objection_selector": objection_selector,
        "evaluator": evaluator,
        "report_gen": report_gen,
        "agent": agent
    }


@app.command()
def nova(
    perfil: Optional[str] = typer.Option(
        None,
        "--perfil",
        "-p",
        help="Profile name to use for the new session"
    )
):
    """Start a new conversation simulation with a client."""
    try:
        managers = get_managers(require_agent=True)
        session_mgr = managers["session_mgr"]
        profile_sys = managers["profile_sys"]
        objection_selector = managers["objection_selector"]
        agent = managers["agent"]
        evaluator = managers["evaluator"]

        if not perfil:
            available = profile_sys.list_available()
            if not available:
                console.print("[red]No profiles available[/red]")
                raise typer.Exit(code=1)

            console.print("\n[bold]Available Profiles:[/bold]")
            for i, p in enumerate(available, 1):
                console.print(f"  {i}. {p}")

            choice = Prompt.ask("Select profile", choices=[str(i) for i in range(1, len(available) + 1)])
            perfil = available[int(choice) - 1]
        else:
            profile = profile_sys.get_by_name(perfil)
            if not profile:
                console.print(f"[red]Profile '{perfil}' not found[/red]")
                raise typer.Exit(code=1)

        session = session_mgr.create_session(profile=perfil)
        profile = profile_sys.get_by_name(perfil)

        console.print(f"\n[bold green]Session started: {session.id}[/bold green]")
        console.print(f"[cyan]Profile: {perfil}[/cyan]")
        console.print(f"[cyan]Personality: {profile.personality}[/cyan]\n")

        objection_count = 0
        max_objections = 10

        while objection_count < max_objections:
            objection = objection_selector.select_next(session)
            if not objection:
                console.print("[yellow]No more objections available[/yellow]")
                break

            objection_count += 1
            console.print(f"\n[bold magenta]Objection {objection_count}/{max_objections}[/bold magenta]")
            console.print(f"[bold]{objection.objection}[/bold]")
            console.print(f"[dim]Category: {objection.category} | Difficulty: {objection.dificuldade}/10[/dim]\n")

            try:
                client_message = agent.generate_response(
                    profile=profile,
                    objection=objection,
                    conversation_history=session.messages
                )
                console.print(f"[cyan]Client:[/cyan] {client_message}")

                msg = Message(
                    role="client",
                    content=client_message,
                    timestamp=datetime.now(),
                    objection_id=objection.id
                )
                session.messages.append(msg)
            except Exception as e:
                console.print(f"[red]Error getting client response: {e}[/red]")
                break

            vendor_response = Prompt.ask("\n[yellow]Your response[/yellow]")

            vendor_msg = Message(
                role="vendor",
                content=vendor_response,
                timestamp=datetime.now(),
                objection_id=objection.id
            )
            session.messages.append(vendor_msg)

            eval_result = evaluator.evaluate_response(vendor_response, objection)
            overcome = eval_result["overcome"]

            status = "contornada" if overcome else "não_contornada"
            usage = ObjectionUsage(
                id=objection.id,
                order=objection_count,
                status=status
            )
            session.objections_used.append(usage)

            if overcome:
                console.print("\n[green]✓ Objection overcome![/green]")
            else:
                reason = eval_result.get("reason", "unknown")
                console.print(f"\n[red]✗ Objection not overcome ({reason})[/red]")

            techniques = eval_result.get("techniques", [])
            if techniques:
                console.print(f"[cyan]Techniques detected: {', '.join(techniques)}[/cyan]")

            if objection_count < max_objections:
                if not Confirm.ask("\nContinue to next objection?"):
                    console.print("\n[yellow]Session ended by user[/yellow]")
                    break

        session_mgr.save_session(session)
        console.print(f"\n[bold green]Session saved: {session.id}[/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted[/yellow]")
        if 'session' in locals() and 'session_mgr' in locals():
            session_mgr.save_session(session)
            console.print(f"Session auto-saved: {session.id}")
        raise typer.Exit(code=0)


@app.command()
def retomar(session_id: str = typer.Argument(..., help="Session ID to resume")):
    """Resume an existing conversation session."""
    try:
        managers = get_managers(require_agent=True)
        session_mgr = managers["session_mgr"]
        profile_sys = managers["profile_sys"]
        objection_selector = managers["objection_selector"]
        agent = managers["agent"]
        evaluator = managers["evaluator"]

        session = session_mgr.load_session(session_id)
        if not session:
            console.print(f"[red]Session '{session_id}' not found[/red]")
            raise typer.Exit(code=1)

        profile = profile_sys.get_by_name(session.profile)
        if not profile:
            console.print(f"[red]Profile '{session.profile}' not found[/red]")
            raise typer.Exit(code=1)

        console.print(f"\n[bold green]Session resumed: {session.id}[/bold green]")
        console.print(f"[cyan]Profile: {session.profile}[/cyan]")
        console.print(f"[cyan]Created: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}[/cyan]")
        console.print(f"[cyan]Objections completed: {len(session.objections_used)}/10[/cyan]\n")

        if session.messages:
            console.print("[bold cyan]Last messages:[/bold cyan]")
            for msg in session.messages[-4:]:
                role = "[cyan]Client[/cyan]" if msg.role == "client" else "[yellow]You[/yellow]"
                console.print(f"{role}: {msg.content[:80]}...")
            console.print()

        objection_count = len(session.objections_used)
        max_objections = 10

        while objection_count < max_objections:
            objection = objection_selector.select_next(session)
            if not objection:
                console.print("[yellow]No more objections available[/yellow]")
                break

            objection_count += 1
            console.print(f"\n[bold magenta]Objection {objection_count}/{max_objections}[/bold magenta]")
            console.print(f"[bold]{objection.objection}[/bold]")
            console.print(f"[dim]Category: {objection.category} | Difficulty: {objection.dificuldade}/10[/dim]\n")

            try:
                client_message = agent.generate_response(
                    profile=profile,
                    objection=objection,
                    conversation_history=session.messages
                )
                console.print(f"[cyan]Client:[/cyan] {client_message}")

                msg = Message(
                    role="client",
                    content=client_message,
                    timestamp=datetime.now(),
                    objection_id=objection.id
                )
                session.messages.append(msg)
            except Exception as e:
                console.print(f"[red]Error getting client response: {e}[/red]")
                break

            vendor_response = Prompt.ask("\n[yellow]Your response[/yellow]")

            vendor_msg = Message(
                role="vendor",
                content=vendor_response,
                timestamp=datetime.now(),
                objection_id=objection.id
            )
            session.messages.append(vendor_msg)

            eval_result = evaluator.evaluate_response(vendor_response, objection)
            overcome = eval_result["overcome"]

            status = "contornada" if overcome else "não_contornada"
            usage = ObjectionUsage(
                id=objection.id,
                order=objection_count,
                status=status
            )
            session.objections_used.append(usage)

            if overcome:
                console.print("\n[green]✓ Objection overcome![/green]")
            else:
                reason = eval_result.get("reason", "unknown")
                console.print(f"\n[red]✗ Objection not overcome ({reason})[/red]")

            techniques = eval_result.get("techniques", [])
            if techniques:
                console.print(f"[cyan]Techniques detected: {', '.join(techniques)}[/cyan]")

            if objection_count < max_objections:
                if not Confirm.ask("\nContinue to next objection?"):
                    console.print("\n[yellow]Session ended by user[/yellow]")
                    break

        session_mgr.save_session(session)
        console.print(f"\n[bold green]Session updated and saved[/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted[/yellow]")
        if 'session' in locals() and 'session_mgr' in locals():
            session_mgr.save_session(session)
            console.print(f"Session auto-saved: {session.id}")
        raise typer.Exit(code=0)


@app.command()
def relatorio(session_id: str = typer.Argument(..., help="Session ID to generate report for")):
    """View performance report for a session."""
    try:
        managers = get_managers()
        session_mgr = managers["session_mgr"]
        report_gen = managers["report_gen"]

        session = session_mgr.load_session(session_id)
        if not session:
            console.print(f"[red]Session '{session_id}' not found[/red]")
            raise typer.Exit(code=1)

        report = report_gen.generate(session)

        console.print()
        console.print(f"[bold cyan]═══════════════════════════════════[/bold cyan]")
        console.print(f"[bold cyan]PERFORMANCE REPORT[/bold cyan]")
        console.print(f"[bold cyan]═══════════════════════════════════[/bold cyan]\n")

        console.print(f"[bold]Session:[/bold] {report.session_id}")
        console.print(f"[bold]Profile:[/bold] {report.profile}")
        console.print(f"[bold]Duration:[/bold] {report.duration} minutes")
        console.print(f"[bold]Date:[/bold] {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

        metrics_table = Table(title="Objection Results", show_header=True, header_style="bold cyan")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="magenta")

        metrics_table.add_row("Total Objections", str(report.total_objections))
        metrics_table.add_row("[green]Overcome[/green]", f"{report.overcome} ({report.score:.1f}%)")
        metrics_table.add_row("[red]Not Overcome[/red]", str(report.not_overcome))
        metrics_table.add_row("[bold yellow]Score[/bold yellow]", f"{report.score:.1f}%")

        console.print(metrics_table)
        console.print()

        if report.techniques:
            console.print("[bold]Techniques Detected:[/bold]")
            for tech in report.techniques:
                console.print(f"  • {tech}")
            console.print()

        if report.recommendations:
            console.print("[bold]Recommendations:[/bold]")
            for rec in report.recommendations:
                console.print(f"  • {rec}")
            console.print()

        console.print("[bold]Objection Details:[/bold]")
        objections_table = Table(show_header=True, header_style="bold cyan")
        objections_table.add_column("Order", style="cyan")
        objections_table.add_column("ID", style="cyan")
        objections_table.add_column("Status", style="magenta")

        for obj in session.objections_used:
            status_str = "[green]Overcome[/green]" if obj.status == "contornada" else "[red]Not Overcome[/red]"
            objections_table.add_row(str(obj.order), obj.id, status_str)

        console.print(objections_table)
        console.print()

    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def listar():
    """List all sessions in a table."""
    try:
        managers = get_managers()
        session_mgr = managers["session_mgr"]

        sessions = session_mgr.list_sessions()

        if not sessions:
            console.print("[yellow]No sessions found[/yellow]")
            return

        table = Table(title="All Sessions", show_header=True, header_style="bold cyan")
        table.add_column("Session ID", style="cyan")
        table.add_column("Profile", style="magenta")
        table.add_column("Created", style="green")
        table.add_column("Duration (min)", style="yellow")
        table.add_column("Objections", style="cyan")

        for session in sorted(sessions, key=lambda s: s.created_at, reverse=True):
            created = session.created_at.strftime("%Y-%m-%d %H:%M")
            objections = f"{len(session.objections_used)}/10"
            table.add_row(
                session.id,
                session.profile,
                created,
                str(session.duration_minutes),
                objections
            )

        console.print()
        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[red]Error listing sessions: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def deletar(session_id: str = typer.Argument(..., help="Session ID to delete")):
    """Delete a session (cannot be undone)."""
    try:
        if not Confirm.ask(f"[red]Delete session '{session_id}'?[/red] This cannot be undone."):
            console.print("[yellow]Deletion cancelled[/yellow]")
            return

        managers = get_managers()
        session_mgr = managers["session_mgr"]

        session = session_mgr.load_session(session_id)
        if not session:
            console.print(f"[red]Session '{session_id}' not found[/red]")
            raise typer.Exit(code=1)

        session_mgr.delete_session(session_id)
        console.print(f"[green]Session '{session_id}' deleted[/green]")

    except Exception as e:
        console.print(f"[red]Error deleting session: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def perfis():
    """List all available profiles."""
    try:
        managers = get_managers()
        profile_sys = managers["profile_sys"]

        profiles = profile_sys.get_all()

        if not profiles:
            console.print("[yellow]No profiles found[/yellow]")
            return

        console.print()
        for i, profile in enumerate(profiles, 1):
            console.print(f"[bold cyan]{i}. {profile.name}[/bold cyan]")
            console.print(f"   [cyan]Personality:[/cyan] {profile.personality}")
            console.print(f"   [cyan]Objectives:[/cyan] {', '.join(profile.objectives)}")
            console.print(f"   [cyan]Objection Priority:[/cyan] {', '.join(profile.objection_priority)}")
            if i < len(profiles):
                console.print()

        console.print()

    except Exception as e:
        console.print(f"[red]Error listing profiles: {e}[/red]")
        raise typer.Exit(code=1)
