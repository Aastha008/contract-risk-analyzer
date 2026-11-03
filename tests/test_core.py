import pytest
from src.core import ContractAnalyzerEngine
from src.models import Rulebook, RuleCreate

@pytest.fixture
def engine(tmp_path):
    return ContractAnalyzerEngine(persist_dir=str(tmp_path))

def test_engine_initialization(engine):
    assert engine is not None
    rules = engine.collection.get()
    assert len(rules["ids"]) >= 4  # Default seeded rules

def test_add_and_get_rules(engine):
    new_rulebook = Rulebook(rules=[
        RuleCreate(rule_id="TEST-99", category="Test", description="Test rule description for unit tests.")
    ])
    engine.add_rules(new_rulebook)
    
    data = engine.collection.get(ids=["TEST-99"])
    assert "TEST-99" in data["ids"]

def test_parse_txt_fallback(engine):
    content = b"This is a test contract containing liability and termination clauses."
    parsed = engine.parse_document(content, "test.txt")
    assert "test contract" in parsed

def test_chunk_contract(engine):
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = engine.chunk_contract(text)
    assert len(chunks) > 0

def test_analyze_contract_mock(engine):
    content = b"Provider shall have unlimited liability for all damages under this vendor agreement."
    report = engine.analyze_contract(content, "vendor_agreement.txt")
    assert report.contract_title == "vendor_agreement.txt"
    assert report.overall_risk_score > 0
    assert len(report.flagged_clauses) > 0
    assert report.flagged_clauses[0].rule_id_matched == "LIAB-01"
