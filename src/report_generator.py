from typing import List, Dict, Optional
from datetime import datetime
from src.models import Session, Report
from src.evaluator import Evaluator

SPIN_MAP = {
    ("financial", "not_addressed"):    ("Implicação",          "Se continuar pagando juros de financiamento por 10 anos, quanto isso representa em dinheiro perdido?"),
    ("financial", "vendor_evaded"):    ("Problema",            "O que mais te incomoda no custo do financiamento que você usa hoje?"),
    ("operational", "not_addressed"):  ("Problema",            "O que te preocupa mais: não ser contemplado rápido ou não ter liquidez no meio do caminho?"),
    ("operational", "vendor_evaded"):  ("Situação",            "Como você planeja usar a carta de crédito quando for contemplado?"),
    ("comparative", "not_addressed"):  ("Necessidade",         "Se eu te mostrar que a taxa do consórcio é 10x menor que os juros do financiamento, faz sentido analisar?"),
    ("comparative", "vendor_evaded"):  ("Necessidade",         "Se eu resolver essa comparação agora com números reais, o que impediria você de avançar?"),
    ("behavioral", "not_addressed"):   ("Situação",            "Você já tem algum planejamento financeiro para a compra do imóvel?"),
    ("behavioral", "vendor_evaded"):   ("Problema",            "O que te travou nas outras vezes em que pensou em investir?"),
    ("default", "not_addressed"):      ("Necessidade",         "Se eu resolver essa dúvida agora, o que impediria você de avançar?"),
    ("default", "vendor_evaded"):      ("Problema",            "O que exatamente está te impedindo de tomar uma decisão hoje?"),
}

SPIN_DEFINITIONS = {
    "Situação":   "Perguntas para entender o contexto atual do cliente — sem julgamento, só diagnóstico.",
    "Problema":   "Perguntas que revelam insatisfações e dificuldades que o cliente já sente.",
    "Implicação": "Perguntas que ampliam o impacto do problema — mostram o custo de não resolver.",
    "Necessidade":"Perguntas que levam o cliente a verbalizar o valor da solução que você oferece.",
}

IMPROVEMENT_DESCRIPTIONS = {
    "explicar_competitividade": "Cite taxas específicas e compare com concorrentes: 'nossa taxa média é X%, abaixo da média do mercado de Y%'.",
    "comparar_com_alternativas": "Mostre a desvantagem da alternativa que o cliente mencionou — juros do financiamento, inflação corroendo a poupança.",
    "reframing": "Reframe o custo como investimento: a taxa paga o grupo gestor que garante a carta de crédito.",
    "seguranca_bacen": "Mencione que consórcios são regulados pelo Banco Central — isso diferencia de investimento informal.",
    "explicar_funcionamento": "Explique o mecanismo em 1 frase simples: 'todo mês o grupo arrecada as parcelas e sorteia quem recebe a carta de crédito'.",
    "mostrar_lance": "Destaque que além do sorteio o cliente pode dar um lance e antecipar a contemplação.",
    "comparar_financiamento": "Compare diretamente: financiamento tem juros de 10-15% ao ano, consórcio tem taxa administrativa de 1-2% ao ano.",
    "comparar_poupança": "Poupança rende menos que a inflação e exige disciplina — consórcio é disciplina automática com poder de compra garantido.",
    "prazo_flexivel": "Mencione que o prazo pode ser encurtado com lances e que a carta pode ser usada após contemplação.",
    "garantia_contemplacao": "Esclareça que todos são contemplados antes do fim do plano — sorteio ou lance.",
}


class ReportGenerator:
    def __init__(self):
        self.evaluator = Evaluator()

    def generate(self, session: Session, objection_bank=None, agent=None) -> Report:
        total = len(session.objections_used)
        overcome_count = sum(1 for obj in session.objections_used if obj.status == "contornada")
        not_overcome_count = total - overcome_count
        score = self.calculate_score(overcome_count, total) if total > 0 else 0
        techniques = self.detect_techniques_in_session(session)
        recommendations = self.generate_recommendations(session)

        objection_analyses = []
        behavioral_patterns = {}
        priority_improvements = []
        spin_recommendations = []
        llm_analysis = {}

        if objection_bank:
            objection_analyses = self._analyze_objection_turns(session, objection_bank)
            behavioral_patterns = self._detect_behavioral_patterns(session, objection_bank)
            priority_improvements = self._build_priority_improvements(session, objection_bank)
            spin_recommendations = self._build_spin_recommendations(session, objection_bank)

        if agent and objection_bank:
            llm_analysis = self._generate_llm_analysis(session, objection_bank, agent, score, overcome_count, total) or {}

        return Report(
            session_id=session.id,
            profile=session.profile,
            duration=session.duration_minutes,
            total_objections=total,
            overcome=overcome_count,
            not_overcome=not_overcome_count,
            score=score,
            techniques=techniques,
            recommendations=recommendations,
            objection_analyses=objection_analyses,
            behavioral_patterns=behavioral_patterns,
            priority_improvements=priority_improvements,
            spin_recommendations=spin_recommendations,
            llm_analysis=llm_analysis,
        )

    def _generate_llm_analysis(self, session: Session, objection_bank, agent, score: float, overcome: int, total: int) -> dict:
        msgs_by_objection: Dict[str, list] = {}
        for msg in session.messages:
            if msg.objection_id:
                msgs_by_objection.setdefault(msg.objection_id, []).append(msg)

        turns = []
        for usage in session.objections_used:
            obj = objection_bank.get_by_id(usage.id)
            msgs = msgs_by_objection.get(usage.id, [])
            vendor_msg = next((m for m in msgs if m.role == "vendor"), None)
            turns.append({
                "objection": obj.objection if obj else usage.id,
                "category": obj.category if obj else "unknown",
                "vendor_response": vendor_msg.content if vendor_msg else "(sem resposta)",
                "overcome": usage.status == "contornada",
            })

        session_data = {
            "profile": session.profile,
            "score": score,
            "overcome": overcome,
            "total": total,
            "turns": turns,
        }
        return agent.generate_report_analysis(session_data)

    def calculate_score(self, overcome: int, total: int) -> float:
        if total == 0:
            return 0.0
        return (overcome / total) * 100.0

    def detect_techniques_in_session(self, session: Session) -> List[str]:
        techniques = set()
        for msg in session.messages:
            if msg.role in ("vendor", "agent"):
                found = self.evaluator.detect_techniques(msg.content)
                techniques.update(found)
        return list(techniques)

    def generate_recommendations(self, session: Session) -> List[str]:
        recommendations = []
        unaddressed = [obj for obj in session.objections_used if obj.status == "não_contornada"]
        if unaddressed:
            objection_ids = [obj.id for obj in unaddressed]
            recommendations.append(f"Trabalhe nestas objeções: {', '.join(objection_ids)}.")
        if not self.detect_techniques_in_session(session):
            recommendations.append("Use mais técnicas comparativas e reframing nas respostas.")
        if not recommendations:
            recommendations.append("Ótimo trabalho! Continue com essa consistência.")
        return recommendations

    def _analyze_objection_turns(self, session: Session, objection_bank) -> List[Dict]:
        analyses = []
        msgs_by_objection: Dict[str, List] = {}
        for msg in session.messages:
            if msg.objection_id:
                msgs_by_objection.setdefault(msg.objection_id, []).append(msg)

        for usage in session.objections_used:
            objection = objection_bank.get_by_id(usage.id)
            msgs = msgs_by_objection.get(usage.id, [])

            client_msg = next((m for m in msgs if m.role == "client"), None)
            vendor_msg = next((m for m in msgs if m.role == "vendor"), None)

            client_excerpt = (client_msg.content[:150] + "...") if client_msg and len(client_msg.content) > 150 else (client_msg.content if client_msg else "—")
            vendor_excerpt = (vendor_msg.content[:150] + "...") if vendor_msg and len(vendor_msg.content) > 150 else (vendor_msg.content if vendor_msg else "—")

            overcome = usage.status == "contornada"
            what_missing = ""
            if not overcome and objection:
                missing_techs = [t for t in objection.técnicas_esperadas if t in IMPROVEMENT_DESCRIPTIONS]
                if missing_techs:
                    what_missing = IMPROVEMENT_DESCRIPTIONS[missing_techs[0]]

            analyses.append({
                "order": usage.order,
                "objection_id": usage.id,
                "objection_text": objection.objection if objection else usage.id,
                "category": objection.category if objection else "unknown",
                "overcome": overcome,
                "client_excerpt": client_excerpt,
                "vendor_excerpt": vendor_excerpt,
                "what_missing": what_missing,
            })

        return analyses

    def _detect_behavioral_patterns(self, session: Session, objection_bank) -> Dict:
        all_techniques_used = set()
        for msg in session.messages:
            if msg.role == "vendor":
                all_techniques_used.update(self.evaluator.detect_techniques(msg.content))

        all_possible = set(self.evaluator.TECHNIQUE_PATTERNS.keys())
        never_used = all_possible - all_techniques_used

        failed_categories: Dict[str, int] = {}
        for usage in session.objections_used:
            if usage.status == "não_contornada":
                obj = objection_bank.get_by_id(usage.id)
                if obj:
                    failed_categories[obj.category] = failed_categories.get(obj.category, 0) + 1

        weakest_category = max(failed_categories, key=failed_categories.get) if failed_categories else None

        return {
            "techniques_used": list(all_techniques_used),
            "techniques_never_used": list(never_used),
            "failed_by_category": failed_categories,
            "weakest_category": weakest_category,
        }

    def _build_priority_improvements(self, session: Session, objection_bank) -> List[str]:
        technique_gap_count: Dict[str, int] = {}
        for usage in session.objections_used:
            if usage.status == "não_contornada":
                obj = objection_bank.get_by_id(usage.id)
                if obj:
                    for tech in obj.técnicas_esperadas:
                        technique_gap_count[tech] = technique_gap_count.get(tech, 0) + 1

        sorted_gaps = sorted(technique_gap_count.items(), key=lambda x: x[1], reverse=True)
        improvements = []
        for tech, _ in sorted_gaps[:3]:
            if tech in IMPROVEMENT_DESCRIPTIONS:
                improvements.append(IMPROVEMENT_DESCRIPTIONS[tech])

        if not improvements:
            improvements.append("Continue praticando — cada simulação revela novos padrões.")

        return improvements

    def _build_spin_recommendations(self, session: Session, objection_bank) -> List[Dict]:
        seen_spin_types = set()
        spin_recs = []

        for usage in session.objections_used:
            if usage.status == "não_contornada":
                obj = objection_bank.get_by_id(usage.id)
                category = obj.category if obj else "default"

                key = (category, "not_addressed")
                if key not in SPIN_MAP:
                    key = ("default", "not_addressed")

                spin_type, example = SPIN_MAP[key]
                if spin_type not in seen_spin_types:
                    seen_spin_types.add(spin_type)
                    spin_recs.append({
                        "type": spin_type,
                        "definition": SPIN_DEFINITIONS.get(spin_type, ""),
                        "example": example,
                        "triggered_by": obj.objection if obj else usage.id,
                    })

        return spin_recs

    def format_report(self, report: Report) -> str:
        output = []
        output.append("=" * 50)
        output.append(f"RELATÓRIO DE DESEMPENHO - {report.session_id}")
        output.append("=" * 50)
        output.append(f"Perfil: {report.profile}")
        output.append(f"Duração: {report.duration} minutos")
        output.append(f"Objeções: {report.total_objections} apresentadas")
        output.append(f"✓ CONTORNADAS: {report.overcome}")
        output.append(f"✗ NÃO CONTORNADAS: {report.not_overcome}")
        output.append(f"SCORE FINAL: {report.score:.1f}%")
        output.append("")
        if report.techniques:
            output.append("TÉCNICAS USADAS:")
            for tech in report.techniques:
                output.append(f"  - {tech}")
        output.append("RECOMENDAÇÕES:")
        for rec in report.recommendations:
            output.append(f"  - {rec}")
        output.append("=" * 50)
        return "\n".join(output)

    def render_html(self, report: Report) -> str:
        score = report.score
        if score >= 85:
            score_color = "#22c55e"
            score_label = "Expert"
        elif score >= 70:
            score_color = "#84cc16"
            score_label = "Competente"
        elif score >= 40:
            score_color = "#f59e0b"
            score_label = "Em Desenvolvimento"
        else:
            score_color = "#ef4444"
            score_label = "Iniciante"

        def objection_cards_html() -> str:
            if not report.objection_analyses:
                return "<p>Nenhuma objeção registrada.</p>"
            cards = []
            for a in report.objection_analyses:
                status_color = "#22c55e" if a["overcome"] else "#ef4444"
                status_icon = "✓" if a["overcome"] else "✗"
                status_text = "Contornou" if a["overcome"] else "Não contornou"
                missing_html = f'<div class="missing"><strong>💡 O que faltou:</strong> {a["what_missing"]}</div>' if a["what_missing"] else ""
                cards.append(f"""
                <div class="card objection-card">
                  <div class="card-header" style="border-left: 4px solid {status_color}">
                    <span class="order">#{a['order']}</span>
                    <span class="objection-text">{a['objection_text']}</span>
                    <span class="status-badge" style="background:{status_color}">{status_icon} {status_text}</span>
                  </div>
                  <div class="card-body">
                    <div class="quote-row"><span class="quote-label">Cliente disse:</span><span class="quote-text">{a['client_excerpt']}</span></div>
                    <div class="quote-row"><span class="quote-label">Você respondeu:</span><span class="quote-text">{a['vendor_excerpt']}</span></div>
                    {missing_html}
                  </div>
                </div>""")
            return "\n".join(cards)

        def patterns_html() -> str:
            bp = report.behavioral_patterns
            if not bp:
                return ""
            used = bp.get("techniques_used", [])
            never = bp.get("techniques_never_used", [])
            weakest = bp.get("weakest_category", "")
            used_pills = "".join(f'<span class="pill pill-green">{t}</span>' for t in used) or '<span class="pill pill-gray">nenhuma</span>'
            never_pills = "".join(f'<span class="pill pill-red">{t}</span>' for t in never) or '<span class="pill pill-gray">todas usadas!</span>'
            weakest_html = f'<p><strong>Categoria mais fraca:</strong> <span class="pill pill-red">{weakest}</span></p>' if weakest else ""
            return f"""
            <div class="card">
              <h2>Padrões de Comportamento</h2>
              <p><strong>Técnicas usadas:</strong><br>{used_pills}</p>
              <p><strong>Técnicas nunca usadas:</strong><br>{never_pills}</p>
              {weakest_html}
            </div>"""

        def improvements_html() -> str:
            if not report.priority_improvements:
                return ""
            items = "".join(f'<div class="improvement-item"><span class="improvement-num">{i+1}</span><span>{imp}</span></div>' for i, imp in enumerate(report.priority_improvements))
            return f"""
            <div class="card">
              <h2>Top {len(report.priority_improvements)} Pontos de Melhoria</h2>
              {items}
            </div>"""

        def spin_html() -> str:
            if not report.spin_recommendations:
                return ""
            items = []
            for rec in report.spin_recommendations:
                items.append(f"""
                <details class="spin-item">
                  <summary><strong>{rec['type']}</strong> — {rec['definition']}</summary>
                  <div class="spin-body">
                    <p><em>Teria ajudado em:</em> "{rec['triggered_by']}"</p>
                    <p><strong>Frase para usar:</strong> "{rec['example']}"</p>
                  </div>
                </details>""")
            return f"""
            <div class="card">
              <h2>SPIN Selling — Para esta sessão</h2>
              <p class="spin-intro">Estas perguntas teriam sido eficazes nas objeções que você não contornou:</p>
              {"".join(items)}
            </div>"""

        def llm_sections_html() -> str:
            llm = report.llm_analysis
            if not llm:
                return patterns_html() + improvements_html() + spin_html()

            def text_card(title: str, key: str) -> str:
                content = llm.get(key, "")
                if not content:
                    return ""
                paragraphs = "".join(f"<p>{p.strip()}</p>" for p in str(content).split("\n") if p.strip())
                return f'<div class="card"><h2>{title}</h2><div class="llm-text">{paragraphs}</div></div>'

            topics = llm.get("study_topics", [])
            study_html = ""
            if topics:
                items = "".join(f'<div class="improvement-item"><span class="improvement-num">{i+1}</span><span>{t}</span></div>' for i, t in enumerate(topics))
                study_html = f'<div class="card"><h2>O que Estudar</h2>{items}</div>'

            return (
                text_card("Análise por Objeção", "objection_analysis")
                + text_card("Diagnóstico de Conhecimento de Produto", "product_knowledge")
                + text_card("Padrões de Comportamento", "behavior_patterns")
                + study_html
                + spin_html()
            )

        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório — {report.session_id}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #1e293b; padding: 24px; }}
  .container {{ max-width: 860px; margin: 0 auto; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 4px; }}
  h2 {{ font-size: 1.1rem; margin-bottom: 16px; color: #334155; }}
  .header {{ background: #1e293b; color: white; padding: 28px 32px; border-radius: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
  .header-meta {{ font-size: 0.85rem; opacity: 0.7; margin-top: 4px; }}
  .score-badge {{ text-align: center; }}
  .score-number {{ font-size: 2.8rem; font-weight: 700; color: {score_color}; line-height: 1; }}
  .score-label {{ font-size: 0.8rem; color: {score_color}; margin-top: 2px; }}
  .stats {{ display: flex; gap: 12px; margin-bottom: 24px; }}
  .stat-card {{ flex: 1; background: white; border-radius: 10px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,.08); text-align: center; }}
  .stat-value {{ font-size: 1.8rem; font-weight: 700; }}
  .stat-label {{ font-size: 0.78rem; color: #64748b; margin-top: 2px; }}
  .card {{ background: white; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-bottom: 20px; }}
  .objection-card {{ padding: 0; overflow: hidden; }}
  .card-header {{ padding: 14px 20px; background: #f8fafc; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
  .order {{ font-weight: 700; color: #64748b; font-size: 0.85rem; }}
  .objection-text {{ flex: 1; font-weight: 600; }}
  .status-badge {{ padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; color: white; white-space: nowrap; }}
  .card-body {{ padding: 16px 20px; display: flex; flex-direction: column; gap: 10px; }}
  .quote-row {{ display: flex; gap: 10px; font-size: 0.88rem; }}
  .quote-label {{ font-weight: 600; color: #64748b; min-width: 120px; }}
  .quote-text {{ color: #334155; }}
  .missing {{ background: #fefce8; border-left: 3px solid #fbbf24; padding: 10px 14px; border-radius: 4px; font-size: 0.88rem; color: #78350f; }}
  .pill {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; margin: 2px; }}
  .pill-green {{ background: #dcfce7; color: #166534; }}
  .pill-red {{ background: #fee2e2; color: #991b1b; }}
  .pill-gray {{ background: #f1f5f9; color: #64748b; }}
  .improvement-item {{ display: flex; gap: 14px; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }}
  .improvement-item:last-child {{ border-bottom: none; }}
  .improvement-num {{ background: #3b82f6; color: white; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0; }}
  .spin-intro {{ color: #64748b; font-size: 0.88rem; margin-bottom: 12px; }}
  .spin-item {{ border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 10px; overflow: hidden; }}
  .spin-item summary {{ padding: 14px 16px; cursor: pointer; list-style: none; background: #f8fafc; font-size: 0.9rem; }}
  .spin-item summary::-webkit-details-marker {{ display: none; }}
  .spin-body {{ padding: 14px 16px; font-size: 0.88rem; line-height: 1.6; border-top: 1px solid #e2e8f0; display: flex; flex-direction: column; gap: 6px; }}
  .llm-text p {{ font-size: 0.9rem; line-height: 1.7; color: #334155; margin-bottom: 10px; }}
  .llm-text p:last-child {{ margin-bottom: 0; }}
  .footer {{ text-align: center; font-size: 0.75rem; color: #94a3b8; margin-top: 32px; padding-bottom: 24px; }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <div>
      <h1>Relatório de Desempenho</h1>
      <div class="header-meta">Perfil: {report.profile} &nbsp;·&nbsp; {now} &nbsp;·&nbsp; {report.duration} min</div>
    </div>
    <div class="score-badge">
      <div class="score-number">{report.score:.0f}%</div>
      <div class="score-label">{score_label}</div>
    </div>
  </div>

  <div class="stats">
    <div class="stat-card"><div class="stat-value">{report.total_objections}</div><div class="stat-label">Objeções</div></div>
    <div class="stat-card"><div class="stat-value" style="color:#22c55e">{report.overcome}</div><div class="stat-label">Contornadas</div></div>
    <div class="stat-card"><div class="stat-value" style="color:#ef4444">{report.not_overcome}</div><div class="stat-label">Não contornadas</div></div>
  </div>

  <div class="card"><h2>Conversa — Objeção por Objeção</h2>{objection_cards_html()}</div>

  {llm_sections_html()}

  <div class="footer">Gerado por Agente Consórcio &nbsp;·&nbsp; {report.session_id}</div>
</div>
</body>
</html>"""
