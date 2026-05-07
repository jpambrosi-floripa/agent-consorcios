import pytest
from unittest.mock import patch, MagicMock
from src.claude_agent import ClaudeAgent
from src.models import Objection, Profile, Message
from datetime import datetime

@pytest.fixture
def mock_anthropic():
    with patch('src.claude_agent.anthropic.Anthropic') as mock:
        yield mock

@pytest.fixture
def agent(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    return ClaudeAgent(api_key="test-key")

def test_build_system_prompt(agent):
    profile = Profile(
        name="Test",
        personality="test",
        objectives=["obj1"],
        objection_priority=["obj1"],
        triggers={}
    )
    prompt = agent._build_system_prompt(profile)
    assert "client" in prompt.lower()
    assert "test" in prompt.lower()

def test_build_objection_instruction(agent):
    objection = Objection(
        id="test",
        category="test",
        objection="Test objection",
        variações=["var1"],
        técnicas_esperadas=["tech1"],
        dificuldade=1
    )
    instruction = agent._build_objection_instruction(objection)
    assert "Test objection" in instruction
    assert "naturally" in instruction.lower()

def test_format_conversation_history(agent):
    messages = [
        Message(role="user", content="Hi", timestamp=datetime.now()),
        Message(role="agent", content="Hello", timestamp=datetime.now())
    ]
    history = agent._format_conversation_history(messages)
    assert "Hi" in history
    assert "Hello" in history

def test_generate_response_calls_api(agent):
    # Mock the API response
    agent.client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Mocked response")]
    )

    profile = Profile(
        name="Test", personality="test",
        objectives=["obj1"], objection_priority=["obj1"]
    )
    objection = Objection(
        id="test", category="test", objection="Test",
        variações=[], técnicas_esperadas=[], dificuldade=1
    )

    response = agent.generate_response(
        profile=profile,
        objection=objection,
        conversation_history=[]
    )

    assert "Mocked response" in response
