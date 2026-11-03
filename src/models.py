from typing import List, Optional
from pydantic import BaseModel, Field

class RuleCreate(BaseModel):
    rule_id: str = Field(..., description="Unique identifier for the corporate rule")
    category: str = Field(..., description="Category such as Liability, Indemnification, Governing Law, Termination")
    description: str = Field(..., description="Detailed description of the acceptable standard or rule requirement")

class Rulebook(BaseModel):
    rules: List[RuleCreate]

class ClauseCitation(BaseModel):
    clause_title: str = Field(..., description="Title or heading of the extracted clause")
    clause_text: str = Field(..., description="Exact excerpt from the contract")
    rule_id_matched: str = Field(..., description="The rule ID this clause was evaluated against")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    explanation: str = Field(..., description="Detailed reasoning why this clause poses the given risk")

class StructuredRiskReport(BaseModel):
    contract_title: str = Field(..., description="Identified title or filename of the contract")
    overall_risk_score: float = Field(..., ge=0.0, le=100.0, description="Calculated aggregate risk score from 0 to 100")
    governing_law: Optional[str] = Field(None, description="Governing law identified in the contract")
    liability_limits: Optional[str] = Field(None, description="Liability cap or limitation of liability terms")
    termination_notice: Optional[str] = Field(None, description="Notice period required for termination")
    flagged_clauses: List[ClauseCitation] = Field(default_factory=list, description="List of evaluated clauses with high or medium risks")

class AnalysisResponse(BaseModel):
    status: str = Field("success", description="Status of the analysis")
    report: StructuredRiskReport
