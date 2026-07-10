# Phase 7 — AI & LLM Design

## Features

| Feature | Module | Endpoint |
|---|---|---|
| ESG report summarizer | `app.ai.assistant.summarize_esg_report` | `POST /api/v1/ai/summarize-report` |
| CSRD/ESRS readiness assistant | `app.ai.assistant.csrd_readiness_summary` | `POST /api/v1/ai/csrd-readiness` |
| Natural-language Q&A over ESG data | `app.ai.assistant.answer_question` | `POST /api/v1/ai/ask` |
| Anomaly explanation | `app.ai.assistant.anomaly_explanation` | `POST /api/v1/ai/anomaly-explanation` |
| Executive summary generator | `app.ai.assistant.generate_executive_summary` | `POST /api/v1/ai/executive-summary` |
| Risk recommendation engine | `app.ai.assistant.recommend_risk_actions` | `POST /api/v1/ai/risk-recommendation` |
| Structured visual insight bundle | `app.ai.assistant.visual_insight_bundle` | (called in-process by dashboard chart panels) |

## Prompt templates

All prompts live in one file, `python/app/ai/prompts.py`, rather than being inlined per
function. `BASE_SYSTEM_PROMPT` is shared by every call and encodes the platform's five
non-negotiable rules (answer only from supplied context, say so when data is insufficient,
respond in the requested language, cite the source dataset/year, never give legal/investment
advice). Feature-specific templates (`QA_TEMPLATE`, `CSRD_READINESS_TEMPLATE`, etc.) fill in
the variable part of the prompt. Centralizing templates means a reviewer can audit exactly
what is sent to the model for every feature in one place — important for CSRD-adjacent AI use.

## Hallucination control

Two layers, implemented in `python/app/ai/grounding.py`:

1. **Prompt-level constraint** — every system prompt explicitly instructs the model to answer
   only from the supplied context and to say so when the context is insufficient (see
   `BASE_SYSTEM_PROMPT` rule 1-2).
2. **Post-hoc numeric grounding check** — `check_grounding()` extracts every number the model's
   answer states and verifies it appears (within a small rounding tolerance) somewhere in the
   context that was sent. If a number can't be traced back to the source data, the response is
   still shown but flagged with a visible warning (`grounded: false`, `warning: "..."`) rather
   than presented as verified fact. This is a heuristic, not a proof of correctness — it catches
   the most common and costly failure mode (fabricated statistics) without needing a second LLM
   call.

Every AI endpoint that answers a data question (`summarize-report`, `executive-summary`,
`risk-recommendation`) returns this grounding metadata alongside the text, so the R dashboard's
AI panels can render an "unverified — check source" badge when `grounded = false`.

## Source-grounded answers

`build_context()` serializes the exact rows/records an answer is allowed to draw from (e.g. the
filtered KPI snapshot the user is currently looking at, or a specific company record) into the
prompt as JSON. The model is never given open-ended access to the full database — only the
slice relevant to the current question — which both improves grounding and reduces token cost.

## Offline / zero-cost fallback

Every AI function has a deterministic, template-based fallback (see `app/ai/llm_client.py`)
that activates automatically when `AZURE_OPENAI_ENDPOINT`/`AZURE_OPENAI_API_KEY` are not
configured, or if the live call fails. Fallback text is clearly prefixed `[Offline mode]` /
`[Offline-Modus]` so users always know whether they're seeing a live AI-generated answer or a
templated placeholder — this is itself a hallucination-control measure: the system never
pretends a canned response is an LLM-verified one.

## GDPR-safe design

- **No personal data enters any prompt.** All grounding context is aggregate national/regional
  statistics or company-level (not individual-level) ESG figures — see
  `docs/02_architecture.md` "Security & GDPR Design" for why the dataset has no personal-data
  surface area to begin with.
- **No conversation history is persisted server-side.** Each `/api/v1/ai/*` call is stateless;
  the R dashboard holds any chat-style context client-side for the session only.
- **Azure OpenAI data residency**: when deployed, the Azure OpenAI resource should be
  provisioned in an EU region (e.g. `germanywestcentral`, `swedencentral`) consistent with the
  rest of the platform's data-residency stance in `docs/02_architecture.md`.
- **No training on customer data**: Azure OpenAI (unlike the public OpenAI API) does not use
  submitted prompts/completions to train models — verify this is still current in your Azure
  OpenAI terms before production use.
- **Right to explanation**: because every AI answer is grounded in explicit, inspectable context
  (see above), a user or auditor can always see exactly what data an AI statement was based on.
