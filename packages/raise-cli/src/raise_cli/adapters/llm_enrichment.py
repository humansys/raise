"""Anthropic-backed implementation of BacklogEnrichmentClient (S9939.3).

Lazy-imports the ``anthropic`` SDK so that the raise-cli package works without
it when cartridge enrichment is not used.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from raise_core.cartridges.business_rules import BusinessRuleProposal, FieldSummary

_SYSTEM_PROMPT = """\
You are a Jira project-management expert. Given a list of custom fields for a \
specific issue type, propose concise, actionable business rules that explain \
when and how each field should be filled. Return a JSON array of objects with \
keys "field_id" (string) and "rule_text" (string). Return ONLY the JSON array \
— no markdown fences, no explanation.
"""


class AnthropicEnrichmentClient:
    """BacklogEnrichmentClient backed by the Anthropic Messages API.

    Args:
        model: Claude model ID (default: claude-sonnet-4-6).
        max_tokens: Maximum tokens per response (default: 1024).
        api_key: Anthropic API key. Uses ``ANTHROPIC_API_KEY`` env var when absent.
    """

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 1024,
        api_key: str | None = None,
    ) -> None:
        self._model = model
        self._max_tokens = max_tokens
        self._api_key = api_key

    async def derive_business_rules(
        self,
        issue_type: str,
        fields: list[FieldSummary],
    ) -> list[BusinessRuleProposal]:
        """Call Claude to derive business rules for *fields* of *issue_type*.

        Raises on API or parse error; the caller (enrich_cartridge_with_business_rules)
        swallows per-issue-type exceptions via best-effort try/except.
        """
        import anthropic  # lazy import — optional dependency

        from raise_core.cartridges.business_rules import BusinessRuleProposal

        client: anthropic.AsyncAnthropic = anthropic.AsyncAnthropic(
            api_key=self._api_key
        )

        fields_payload = [
            {
                "field_id": f.field_id,
                "name": f.name,
                "schema_type": f.schema_type,
                "allowed_values": f.allowed_values,
            }
            for f in fields
        ]
        user_content = f"Issue type: {issue_type}\n\nCustom fields:\n" + json.dumps(
            fields_payload, indent=2, ensure_ascii=False
        )

        response = await client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        raw_text: str = response.content[0].text  # type: ignore[union-attr]
        proposals_raw: list[Any] = json.loads(raw_text)
        return [
            BusinessRuleProposal(
                field_id=p["field_id"],
                rule_text=p["rule_text"],
            )
            for p in proposals_raw
            if isinstance(p, dict) and "field_id" in p and "rule_text" in p
        ]
