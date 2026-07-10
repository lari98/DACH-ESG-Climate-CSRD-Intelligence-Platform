from app.ai.assistant import generate_executive_summary, recommend_risk_actions, summarize_esg_report
from app.ai.grounding import build_context, check_grounding


def test_check_grounding_flags_fabricated_number():
    context = build_context({"co2_emissions_mt": 670, "year": 2023})
    answer = "Emissions were 999999 Mt in 2023."  # 999999 not in context
    result = check_grounding(answer, context)
    assert not result.grounded
    assert "999999" in " ".join(result.unmatched_numbers)


def test_check_grounding_passes_when_numbers_match():
    context = build_context({"co2_emissions_mt": 670.5, "year": 2023})
    answer = "Emissions were about 670.5 Mt in 2023."
    result = check_grounding(answer, context)
    assert result.grounded


def test_summarize_esg_report_offline():
    result = summarize_esg_report("Sample report text about emissions.", lang="en")
    assert "summary" in result and isinstance(result["grounded"], bool)


def test_generate_executive_summary_offline():
    result = generate_executive_summary({"co2_emissions_mt": 670, "renewable_share_pct": 52}, lang="en")
    assert "summary" in result


def test_recommend_risk_actions_offline():
    result = recommend_risk_actions({"composite_climate_risk_score": 6.5}, lang="de")
    assert "recommendation" in result
