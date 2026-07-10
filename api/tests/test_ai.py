from app.ai.assistant import answer_question, visual_insight_bundle


def test_answer_question_offline_fallback_en():
    ans = answer_question("What is the CO2 trend in Germany?", lang="en")
    assert isinstance(ans, str) and len(ans) > 0


def test_answer_question_offline_fallback_de():
    ans = answer_question("Wie ist der CO2-Trend in Deutschland?", lang="de")
    assert isinstance(ans, str) and len(ans) > 0


def test_visual_insight_bundle_bilingual():
    en = visual_insight_bundle("CO2 emissions", -5.2, lang="en")
    de = visual_insight_bundle("CO2-Emissionen", -5.2, lang="de")
    assert "decreased" in en["what_changed"]
    assert "gesunken" in de["what_changed"]
    assert set(en.keys()) == {
        "what_changed", "why_it_matters", "risk_explanation",
        "business_impact", "recommended_action", "csrd_implication",
    }
