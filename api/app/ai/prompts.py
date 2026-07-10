"""Centralized prompt templates for every AI feature.

Keeping templates in one file (rather than inline strings scattered across
assistant.py) makes prompt engineering auditable — required for CSRD-adjacent AI
use where a reviewer should be able to see exactly what was asked of the model.
Every template enforces: (1) answer only from supplied context/data, (2) say so
explicitly if the answer isn't in the context, (3) respond in the requested
language. This is the core of the hallucination-control strategy (see
app/ai/grounding.py and docs/05_ai_llm_design.md).
"""
from __future__ import annotations

BASE_SYSTEM_PROMPT = (
    "You are an ESG, climate risk, and CSRD/ESRS reporting analyst for companies operating in "
    "Germany, Austria, and Switzerland (DACH). Rules you must follow:\n"
    "1. Answer ONLY using the data/context provided in the user message. Do not invent figures.\n"
    "2. If the context does not contain enough information to answer, say so explicitly rather "
    "than guessing.\n"
    "3. Respond in the language requested (English or German), in concise business language.\n"
    "4. When citing a number, state which dataset/year it came from.\n"
    "5. Never provide legal or investment advice — frame CSRD guidance as informational, not "
    "compliance sign-off."
)

QA_TEMPLATE = (
    "Context (grounding data, JSON):\n{context}\n\n"
    "Question ({lang}): {question}\n\n"
    "Answer using only the context above. If insufficient, say so."
)

ESG_REPORT_SUMMARY_TEMPLATE = (
    "Summarize the following ESG report excerpt in {lang} for a time-pressed executive. "
    "Use at most 5 sentences. Extract: reporting scope, key metrics mentioned, and any explicitly "
    "stated targets or gaps. Do not add information not present in the text.\n\n"
    "Report excerpt:\n{report_text}"
)

CSRD_READINESS_TEMPLATE = (
    "Company data (JSON): {company}\n\n"
    "In {lang}, write a 2-3 sentence CSRD/ESRS audit-readiness assessment. Reference the actual "
    "csrd_readiness_score and reporting_gaps_count values given. Recommend one concrete next step."
)

ANOMALY_EXPLANATION_TEMPLATE = (
    "Anomaly detected (JSON): {anomaly}\n\n"
    "In {lang}, explain in plain business language what this anomaly means, name 1-2 plausible "
    "causes (data issue vs. genuine change), and state the recommended action. Do not speculate "
    "beyond what the anomaly record supports."
)

EXECUTIVE_SUMMARY_TEMPLATE = (
    "KPI snapshot (JSON): {kpis}\n\n"
    "In {lang}, write a 4-6 sentence executive summary covering: current position, trend "
    "direction, biggest risk, and one recommended priority. Business tone, no jargon, grounded "
    "only in the KPI snapshot provided."
)

RISK_RECOMMENDATION_TEMPLATE = (
    "Risk profile (JSON): {risk_profile}\n\n"
    "In {lang}, recommend up to 3 prioritized risk-mitigation actions, ranked by impact. Each "
    "recommendation must reference a specific value from the risk profile that justifies it."
)
