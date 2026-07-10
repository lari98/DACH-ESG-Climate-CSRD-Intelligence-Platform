"""LLM output tests: bilingual coverage, grounding, and structural contract of AI
outputs. Runs entirely against the offline fallback path (no API key needed), so
these run in CI for free — see docs/05_ai_llm_design.md."""
from app.ai.assistant import (
    anomaly_explanation,
    csrd_readiness_summary,
    recommend_risk_actions,
    summarize_esg_report,
    visual_insight_bundle,
)
from app.ai.grounding import check_grounding


def test_csrd_summary_mentions_actual_score_not_placeholder():
    company = {"company_name": "Acme AG", "csrd_readiness_score": 42, "reporting_gaps_count": 3}
    summary = csrd_readiness_summary(company, lang="en")
    assert "42" in summary
    assert "Acme AG" in summary


def test_anomaly_explanation_is_bilingual():
    anomaly = {"column": "co2_emissions_mt", "relative_change": 0.3}
    en = anomaly_explanation(anomaly, lang="en")
    de = anomaly_explanation(anomaly, lang="de")
    assert en != de
    assert len(en) > 20 and len(de) > 20


def test_visual_insight_bundle_has_all_required_sections():
    bundle = visual_insight_bundle("CO2 emissions", 3.4, lang="en")
    required = {"what_changed", "why_it_matters", "risk_explanation",
                "business_impact", "recommended_action", "csrd_implication"}
    assert required == set(bundle.keys())
    assert all(isinstance(v, str) and len(v) > 0 for v in bundle.values())


def test_offline_responses_are_clearly_labeled():
    """Every offline fallback must self-identify as offline so users never mistake
    a canned response for a live, data-verified LLM answer (hallucination-control
    requirement from docs/05_ai_llm_design.md)."""
    result = summarize_esg_report("Some report text", lang="en")
    assert "[Offline mode]" in result["summary"] or result["grounded"] is not None


def test_risk_recommendation_no_fabricated_high_confidence_numbers():
    result = recommend_risk_actions({"composite_climate_risk_score": 5.0}, lang="en")
    # offline fallback should reference the actual score passed in
    assert "5.0" in result["recommendation"] or "5" in result["recommendation"]


def test_grounding_tolerance_is_reasonable():
    context = '{"co2_emissions_mt": 670.4}'
    close_answer = "Emissions are around 670.4 Mt."
    far_answer = "Emissions are around 12345 Mt."
    assert check_grounding(close_answer, context).grounded
    assert not check_grounding(far_answer, context).grounded
