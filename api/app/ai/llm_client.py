"""Thin LLM client abstraction.

Uses Azure OpenAI when AZURE_OPENAI_* settings are configured; otherwise falls back
to a deterministic, template-based local generator so every AI panel in the
dashboard keeps working with zero cost and zero cloud dependency (see
docs/02_architecture.md "Local Development Option").
"""
from __future__ import annotations

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._azure_available = bool(
            self.settings.azure_openai_endpoint and self.settings.azure_openai_api_key
        )
        if self._azure_available:
            try:
                from openai import AzureOpenAI  # imported lazily; optional dependency

                self._client = AzureOpenAI(
                    azure_endpoint=self.settings.azure_openai_endpoint,
                    api_key=self.settings.azure_openai_api_key,
                    api_version="2024-02-15-preview",
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Azure OpenAI client init failed (%s); using local fallback", exc)
                self._azure_available = False

    @property
    def is_live(self) -> bool:
        return self._azure_available

    def complete(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if not self._azure_available:
            return fallback
        try:
            resp = self._client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=400,
            )
            return resp.choices[0].message.content or fallback
        except Exception as exc:  # noqa: BLE001
            logger.warning("Azure OpenAI call failed (%s); using local fallback", exc)
            return fallback


_client_singleton: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = LLMClient()
    return _client_singleton
