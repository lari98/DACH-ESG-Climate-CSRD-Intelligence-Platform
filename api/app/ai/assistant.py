"""ESG / CSRD AI assistant functions — bilingual (EN/DE) summarization, CSRD readiness
narrative, and NL Q&A. Every function has a fully offline, deterministic fallback path
so the dashboard's AI panels work with $0 cost even with no Azure OpenAI deployment."""
from __future__ import annotations

from app.ai.grounding import build_context, check_grounding
from app.ai.llm_client import get_llm_client
from app.ai.prompts import (
    ESG_REPORT_SUMMARY_TEMPLATE,
    EXECUTIVE_SUMMARY_TEMPLATE,
    RISK_RECOMMENDATION_TEMPLATE,
)

SYSTEM_PROMPT = (
    "You are an ESG, climate risk, and CSRD reporting analyst for companies operating in "
    "Germany, Austria, and Switzerland. Answer concisely, in business language, in the "
    "requested language (English or German). Ground answers only in the data provided."
)


def answer_question(question: str, lang: str = "en", context: str | None = None) -> str:
    client = get_llm_client()
    user_prompt = f"Context:\n{context or 'No additional context provided.'}\n\nQuestion ({lang}): {question}"
    fallback = (
        f"[Offline mode] I can't reach the Azure OpenAI service right now, so here is a "
        f"general answer based on known DACH trends: emissions have been falling across "
        f"Germany, Austria, and Switzerland since 2000, driven by renewable energy growth "
        f"and the German Energiewende. Configure AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY "
        f"to enable live, data-grounded answers."
        if lang == "en"
        else
        f"[Offline-Modus] Der Azure-OpenAI-Dienst ist derzeit nicht erreichbar. Allgemeine "
        f"Antwort basierend auf bekannten DACH-Trends: Die Emissionen sinken seit 2000 in "
        f"Deutschland, Österreich und der Schweiz, getrieben durch den Ausbau erneuerbarer "
        f"Energien und die Energiewende. Konfigurieren Sie AZURE_OPENAI_ENDPOINT / "
        f"AZURE_OPENAI_API_KEY für datenbasierte Live-Antworten."
    )
    return client.complete(SYSTEM_PROMPT, user_prompt, fallback)


def csrd_readiness_summary(company: dict, lang: str = "en") -> str:
    client = get_llm_client()
    user_prompt = (
        f"Summarize CSRD audit readiness for this company in 2-3 sentences, in {lang}: {company}"
    )
    score = company.get("csrd_readiness_score", 0)
    gaps = company.get("reporting_gaps_count", 0)
    name = company.get("company_name", "This company")
    fallback = (
        f"{name} has a CSRD readiness score of {score:.0f}% with {gaps} open reporting gap(s). "
        f"{'Prioritize closing Scope 3 and governance gaps before the next reporting wave.' if score < 60 else 'Readiness is solid; focus on assurance-quality evidence for the audit trail.'}"
        if lang == "en"
        else
        f"{name} hat eine CSRD-Bereitschaft von {score:.0f}% mit {gaps} offenen Berichtslücken. "
        f"{'Priorisieren Sie das Schließen von Scope-3- und Governance-Lücken vor der nächsten Berichtswelle.' if score < 60 else 'Die Bereitschaft ist solide; konzentrieren Sie sich auf prüfungsfeste Nachweise für den Audit-Trail.'}"
    )
    return client.complete(SYSTEM_PROMPT, user_prompt, fallback)


def anomaly_explanation(anomaly: dict, lang: str = "en") -> str:
    client = get_llm_client()
    user_prompt = f"Explain this data anomaly for a non-technical ESG stakeholder, in {lang}: {anomaly}"
    col = anomaly.get("column", "a metric")
    change = anomaly.get("relative_change", 0) * 100
    fallback = (
        f"A change of {change:.1f}% was detected in {col}, larger than the expected tolerance. "
        f"This could reflect a genuine policy/market shift, a reporting boundary change, or a "
        f"data quality issue — it has been withheld from the dashboard pending review."
        if lang == "en"
        else
        f"Eine Veränderung von {change:.1f}% wurde bei {col} festgestellt, größer als die "
        f"erwartete Toleranz. Dies kann eine echte Politik-/Marktverschiebung, eine geänderte "
        f"Berichtsgrenze oder ein Datenqualitätsproblem widerspiegeln — die Daten wurden bis zur "
        f"Prüfung vom Dashboard zurückgehalten."
    )
    return client.complete(SYSTEM_PROMPT, user_prompt, fallback)


def visual_insight_bundle(metric_name: str, delta_pct: float, lang: str = "en") -> dict:
    """Generates the standard AI insight bundle requested by the dashboard spec:
    What changed / Why it matters / Risk explanation / Business impact / Recommended
    action / CSRD implication — bilingual, deterministic (no LLM call needed for this
    structured template; kept fast + free for every chart interaction)."""
    direction_en = "increased" if delta_pct > 0 else "decreased"
    direction_de = "gestiegen" if delta_pct > 0 else "gesunken"
    if lang == "de":
        return {
            "what_changed": f"{metric_name} ist um {abs(delta_pct):.1f}% {direction_de}.",
            "why_it_matters": "Diese Kennzahl beeinflusst direkt die CSRD-Offenlegungspflichten und die Klimarisikobewertung.",
            "risk_explanation": "Große Verschiebungen können auf regulatorische oder marktbedingte Veränderungen hindeuten.",
            "business_impact": "Kann Kapitalkosten, Versicherungsprämien oder Investorenwahrnehmung beeinflussen.",
            "recommended_action": "Trend mit Fachabteilung validieren und in den nächsten CSRD-Bericht aufnehmen.",
            "csrd_implication": "Sollte im Übergangsplan und in den Zielpfaden dokumentiert werden.",
        }
    return {
        "what_changed": f"{metric_name} {direction_en} by {abs(delta_pct):.1f}%.",
        "why_it_matters": "This metric directly feeds CSRD disclosure obligations and climate risk scoring.",
        "risk_explanation": "Large shifts can signal regulatory or market-driven change worth investigating.",
        "business_impact": "May affect cost of capital, insurance premiums, or investor perception.",
        "recommended_action": "Validate the trend with the relevant business unit and reflect it in the next CSRD report.",
        "csrd_implication": "Should be documented in the transition plan and target pathways.",
    }


# --- Phase 7 additions: report summarizer, executive summary, risk recommendations ---
# Each function follows the same pattern as the functions above: a prompt-templated
# LLM call (see app/ai/prompts.py) with a deterministic offline fallback, plus a
# source-grounding check (app/ai/grounding.py) so any numeric claim in the response
# can be flagged if it doesn't trace back to the supplied context.

def summarize_esg_report(report_text: str, lang: str = "en") -> dict:
    """ESG report summarizer — condenses a pasted/extracted ESG report excerpt into
    an executive-readable summary, grounded strictly in the supplied text."""
    client = get_llm_client()
    user_prompt = ESG_REPORT_SUMMARY_TEMPLATE.format(lang=lang, report_text=report_text[:6000])
    fallback = (
        f"[Offline mode] Report excerpt received ({len(report_text)} characters). Configure "
        f"Azure OpenAI for an AI-generated summary. In the meantime, review the excerpt manually "
        f"for reporting scope, key metrics, and stated targets."
        if lang == "en" else
        f"[Offline-Modus] Berichtsauszug empfangen ({len(report_text)} Zeichen). Konfigurieren Sie "
        f"Azure OpenAI für eine KI-generierte Zusammenfassung. Prüfen Sie den Auszug in der "
        f"Zwischenzeit manuell auf Berichtsumfang, Kennzahlen und genannte Ziele."
    )
    context = build_context({"report_excerpt": report_text[:6000]})
    summary = client.complete(SYSTEM_PROMPT, user_prompt, fallback)
    grounding = check_grounding(summary, context)
    return {"summary": summary, "grounded": grounding.grounded, "warning": grounding.warning}


def generate_executive_summary(kpis: dict, lang: str = "en") -> dict:
    """Executive summary generator — turns a KPI snapshot (e.g. the Executive
    Overview tab's current filter state) into a short narrative for leadership."""
    client = get_llm_client()
    context = build_context(kpis)
    user_prompt = EXECUTIVE_SUMMARY_TEMPLATE.format(lang=lang, kpis=context)
    co2 = kpis.get("co2_emissions_mt")
    renew = kpis.get("renewable_share_pct")
    fallback = (
        f"[Offline mode] Current position: {co2} Mt CO2, {renew}% renewable share. "
        f"Configure Azure OpenAI for a full narrative executive summary grounded in live KPIs."
        if lang == "en" else
        f"[Offline-Modus] Aktuelle Position: {co2} Mt CO2, {renew}% Anteil Erneuerbare. "
        f"Konfigurieren Sie Azure OpenAI für eine vollständige, datenbasierte Management-Zusammenfassung."
    )
    summary = client.complete(SYSTEM_PROMPT, user_prompt, fallback)
    grounding = check_grounding(summary, context)
    return {"summary": summary, "grounded": grounding.grounded, "warning": grounding.warning}


def recommend_risk_actions(risk_profile: dict, lang: str = "en") -> dict:
    """Risk recommendation engine — ranks concrete mitigation actions from a
    region/company risk profile (physical/transition/flood/heat scores)."""
    client = get_llm_client()
    context = build_context(risk_profile)
    user_prompt = RISK_RECOMMENDATION_TEMPLATE.format(lang=lang, risk_profile=context)
    composite = risk_profile.get("composite_climate_risk_score", 0)
    fallback = (
        f"[Offline mode] Composite risk score is {composite}/10. General guidance: prioritize "
        f"physical-risk adaptation if physical_risk_score is high, and document transition-risk "
        f"exposure in the CSRD transition plan if transition_risk_score is high."
        if lang == "en" else
        f"[Offline-Modus] Der zusammengesetzte Risiko-Score beträgt {composite}/10. Allgemeine "
        f"Empfehlung: Priorisieren Sie Anpassungsmaßnahmen bei hohem physical_risk_score und "
        f"dokumentieren Sie die Übergangsrisiken im CSRD-Transitionsplan bei hohem transition_risk_score."
    )
    recommendation = client.complete(SYSTEM_PROMPT, user_prompt, fallback)
    grounding = check_grounding(recommendation, context)
    return {"recommendation": recommendation, "grounded": grounding.grounded, "warning": grounding.warning}
