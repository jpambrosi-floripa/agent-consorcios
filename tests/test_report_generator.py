import pytest
from src.report_generator import ReportGenerator
from src.models import Session, Message, ObjectionUsage
from datetime import datetime

def test_generate_report():
    session = Session(
        id="session-001",
        profile="investment-focused",
        messages=[
            Message(role="user", content="Hi", timestamp=datetime.now()),
            Message(role="agent", content="Hi there", timestamp=datetime.now())
        ],
        objections_used=[
            ObjectionUsage(id="taxa", order=1, status="contornada"),
            ObjectionUsage(id="rentabilidade", order=2, status="não_contornada")
        ]
    )

    generator = ReportGenerator()
    report = generator.generate(session)

    assert report.session_id == "session-001"
    assert report.total_objections == 2
    assert report.overcome == 1
    assert report.not_overcome == 1
    assert report.score == 50.0

def test_calculate_score():
    generator = ReportGenerator()
    score = generator.calculate_score(overcome=3, total=4)
    assert score == 75.0

def test_detect_techniques_in_conversation():
    session = Session(
        id="session-001",
        profile="investment-focused",
        messages=[
            Message(role="user", content="How much?", timestamp=datetime.now()),
            Message(role="agent", content="Compared with alternatives", timestamp=datetime.now()),
            Message(role="agent", content="You can see the difference", timestamp=datetime.now())
        ]
    )

    generator = ReportGenerator()
    techniques = generator.detect_techniques_in_session(session)
    assert len(techniques) > 0
