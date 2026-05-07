from typing import List
import re
from src.models import Session, Report
from src.evaluator import Evaluator

class ReportGenerator:
    def __init__(self):
        self.evaluator = Evaluator()

    def generate(self, session: Session) -> Report:
        total = len(session.objections_used)
        overcome = sum(
            1 for obj in session.objections_used
            if obj.status == "contornada"
        )
        not_overcome = total - overcome

        score = self.calculate_score(overcome, total) if total > 0 else 0
        techniques = self.detect_techniques_in_session(session)
        recommendations = self.generate_recommendations(session)

        return Report(
            session_id=session.id,
            profile=session.profile,
            duration=session.duration_minutes,
            total_objections=total,
            overcome=overcome,
            not_overcome=not_overcome,
            score=score,
            techniques=techniques,
            recommendations=recommendations
        )

    def calculate_score(self, overcome: int, total: int) -> float:
        if total == 0:
            return 0.0
        return (overcome / total) * 100.0

    def detect_techniques_in_session(self, session: Session) -> List[str]:
        """Aggregate techniques used across all vendor messages"""
        techniques = set()

        for msg in session.messages:
            if msg.role == "agent":  # Agent/vendor response messages
                found = self.evaluator.detect_techniques(msg.content)
                techniques.update(found)

        return list(techniques)

    def generate_recommendations(self, session: Session) -> List[str]:
        """Generate improvement recommendations based on performance"""
        recommendations = []

        # Check for unaddressed objections
        unaddressed = [
            obj for obj in session.objections_used
            if obj.status == "não_contornada"
        ]

        if len(unaddressed) > 0:
            objection_ids = [obj.id for obj in unaddressed]
            recommendations.append(
                f"Work on: {', '.join(objection_ids)}. These objections were not addressed."
            )

        # Check if techniques were used
        if not self.detect_techniques_in_session(session):
            recommendations.append(
                "Try using more comparative and reframing techniques."
            )

        # Score-based recommendations
        score = (session.duration_minutes / 45) * 100 if session.duration_minutes else 0
        if score < 50:
            recommendations.append(
                "Try to keep conversations longer - more time for building rapport."
            )

        if not recommendations:
            recommendations.append("Great job! Keep up the momentum.")

        return recommendations

    def format_report(self, report: Report) -> str:
        """Format report as readable text"""
        output = []
        output.append("=" * 50)
        output.append(f"RELATÓRIO DE DESEMPENHO - {report.session_id}")
        output.append("=" * 50)
        output.append("")
        output.append(f"Perfil: {report.profile}")
        output.append(f"Duração: {report.duration} minutos")
        output.append(f"Objeções: {report.total_objections} apresentadas")
        output.append("")
        output.append(f"✓ CONTORNADAS: {report.overcome}")
        output.append(f"✗ NÃO CONTORNADAS: {report.not_overcome}")
        output.append("")
        output.append(f"SCORE FINAL: {report.score:.1f}%")
        output.append("")

        if report.techniques:
            output.append("TÉCNICAS USADAS:")
            for tech in report.techniques:
                output.append(f"  - {tech}")
            output.append("")

        output.append("RECOMENDAÇÕES:")
        for rec in report.recommendations:
            output.append(f"  - {rec}")

        output.append("")
        output.append("=" * 50)

        return "\n".join(output)
