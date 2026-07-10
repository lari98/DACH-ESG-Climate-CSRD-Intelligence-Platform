"""Source-grounding + hallucination-control utilities.

Two complementary mechanisms:
1. `build_context()` — serializes the exact data rows an answer is allowed to draw
   from into the prompt, so the model has no reason to invent numbers.
2. `check_grounding()` — a lightweight post-hoc check that flags a response as
   "ungrounded" if it contains numeric values that don't appear anywhere in the
   supplied context. This doesn't guarantee zero hallucination (no cheap check
   can), but it catches the most common failure mode — fabricated statistics —
   and lets the caller attach a visible warning badge in the UI instead of
   presenting an unverified number as fact.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass


def build_context(data: dict | list) -> str:
    """Serializes grounding data deterministically (sorted keys) for prompt inclusion."""
    return json.dumps(data, sort_keys=True, default=str)


@dataclass
class GroundingResult:
    grounded: bool
    unmatched_numbers: list[str]
    warning: str | None = None


_NUMBER_RE = re.compile(r"-?\d+\.?\d*")


def check_grounding(answer: str, context: str, tolerance: float = 0.5) -> GroundingResult:
    """Flags numeric claims in `answer` that don't approximately match any number
    in `context`. `tolerance` allows small rounding differences (e.g. 673.2 vs 673)."""
    answer_numbers = [float(n) for n in _NUMBER_RE.findall(answer) if n not in ("", "-", ".")]
    context_numbers = [float(n) for n in _NUMBER_RE.findall(context) if n not in ("", "-", ".")]

    unmatched = []
    for n in answer_numbers:
        if not any(abs(n - c) <= tolerance for c in context_numbers):
            unmatched.append(str(n))

    grounded = len(unmatched) == 0
    warning = None
    if not grounded:
        warning = (
            f"{len(unmatched)} numeric value(s) in this answer could not be verified against "
            f"the source data ({', '.join(unmatched[:5])}). Treat with caution."
        )
    return GroundingResult(grounded=grounded, unmatched_numbers=unmatched, warning=warning)


def grounded_complete(client, system_prompt: str, user_prompt: str, fallback: str, context: str) -> tuple[str, GroundingResult]:
    """Wraps LLMClient.complete() with a grounding check on the result."""
    answer = client.complete(system_prompt, user_prompt, fallback)
    result = check_grounding(answer, context)
    return answer, result
