"""AI endpoints — thin wrappers around app.ai.assistant, consumed by the R Shiny
'AI ESG Assistant' tab (r_dashboard/app/modules/mod_ai_assistant.R)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.assistant import (
    answer_question,
    anomaly_explanation,
    csrd_readiness_summary,
    generate_executive_summary,
    recommend_risk_actions,
    summarize_esg_report,
)
from app.api.deps import get_db
from app.db.models import CompanyESG

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class AskRequest(BaseModel):
    question: str
    lang: str = "en"


class AskResponse(BaseModel):
    answer: str


class CSRDRequest(BaseModel):
    company_id: str
    lang: str = "en"


class CSRDResponse(BaseModel):
    summary: str


class AnomalyRequest(BaseModel):
    column: str
    relative_change: float
    lang: str = "en"


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    return AskResponse(answer=answer_question(req.question, req.lang))


@router.post("/csrd-readiness", response_model=CSRDResponse)
def csrd_readiness(req: CSRDRequest, db: Session = Depends(get_db)) -> CSRDResponse:
    row = db.query(CompanyESG).filter(CompanyESG.company_id == req.company_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Company not found")
    company = {c.name: getattr(row, c.name) for c in CompanyESG.__table__.columns}
    return CSRDResponse(summary=csrd_readiness_summary(company, req.lang))


@router.post("/anomaly-explanation", response_model=CSRDResponse)
def explain_anomaly(req: AnomalyRequest) -> CSRDResponse:
    summary = anomaly_explanation(
        {"column": req.column, "relative_change": req.relative_change}, req.lang
    )
    return CSRDResponse(summary=summary)


# --- Phase 7 additions: report summarizer, executive summary, risk recommendations ---

class GroundedResponse(BaseModel):
    text: str
    grounded: bool
    warning: str | None = None


class ReportSummaryRequest(BaseModel):
    report_text: str
    lang: str = "en"


@router.post("/summarize-report", response_model=GroundedResponse)
def summarize_report(req: ReportSummaryRequest) -> GroundedResponse:
    result = summarize_esg_report(req.report_text, req.lang)
    return GroundedResponse(text=result["summary"], grounded=result["grounded"], warning=result["warning"])


class ExecutiveSummaryRequest(BaseModel):
    kpis: dict
    lang: str = "en"


@router.post("/executive-summary", response_model=GroundedResponse)
def executive_summary(req: ExecutiveSummaryRequest) -> GroundedResponse:
    result = generate_executive_summary(req.kpis, req.lang)
    return GroundedResponse(text=result["summary"], grounded=result["grounded"], warning=result["warning"])


class RiskRecommendationRequest(BaseModel):
    risk_profile: dict
    lang: str = "en"


@router.post("/risk-recommendation", response_model=GroundedResponse)
def risk_recommendation(req: RiskRecommendationRequest) -> GroundedResponse:
    result = recommend_risk_actions(req.risk_profile, req.lang)
    return GroundedResponse(text=result["recommendation"], grounded=result["grounded"], warning=result["warning"])
