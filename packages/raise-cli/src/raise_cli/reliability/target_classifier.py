"""TargetClassifier — LLM-backed inference classification (RAISE-11491).

Architecture:
- LlmProvider: @runtime_checkable Protocol with single method classify_batch_raw()
  — the BYOK extension seam (RAISE-11585). Adding OpenRouterProvider is purely additive.
- AnthropicProvider: concrete implementation using Anthropic SDK Batch API.
- TargetClassifier: orchestrates credential resolution, prompt building, caching, and
  graceful degradation when no API key is configured.

Lazy-import pattern: ``import anthropic`` occurs inside AnthropicProvider methods,
matching the precedent in adapters/llm_enrichment.py. The raise-cli package works
without ``anthropic`` installed when the lens does not use inference.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

__all__ = [
    "AnthropicProvider",
    "ConfigurationError",
    "LlmProvider",
    "TargetClassifier",
    "_resolve_credential",
]

_DEFAULT_HERMES_PATH = str(Path.home() / ".hermes" / "auth.json")

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ConfigurationError(ValueError):
    """Raised when an explicitly-provided API key is invalid or rejected by the API.

    This error surfaces at the time of the actual API call, NOT at construction.
    Callers that resolve credentials lazily (e.g. from env or hermes) will see
    graceful degradation (no provider) rather than ConfigurationError.
    """


# ---------------------------------------------------------------------------
# Credential resolver (D2 — three-tier chain)
# ---------------------------------------------------------------------------


def _resolve_credential(
    config: ClassifierConfig,
    hermes_path: str = _DEFAULT_HERMES_PATH,
) -> str | None:
    """Resolve the Anthropic API key from the three-tier priority chain (D2).

    Priority:
    1. ``config.api_key`` — explicit override (highest priority)
    2. ``ANTHROPIC_API_KEY`` environment variable
    3. ``~/.hermes/auth.json`` → ``credential_pool.anthropic``

    Returns:
        The resolved key string, or None if none of the three tiers yield a value.
        Returning None is NOT an error — the caller decides whether to degrade.
    """
    # Tier 1: explicit config key
    if config.api_key:
        return config.api_key

    # Tier 2: environment variable
    env_key = os.environ.get("ANTHROPIC_API_KEY")
    if env_key:
        return env_key

    # Tier 3: ~/.hermes/auth.json credential_pool.anthropic
    hermes = Path(hermes_path)
    if hermes.is_file():
        try:
            data = json.loads(hermes.read_text())
            pool = data.get("credential_pool", {})
            hermes_key = pool.get("anthropic")
            if hermes_key:
                return str(hermes_key)
        except (json.JSONDecodeError, OSError):
            pass  # Hermes read failure is non-fatal — fall through to None

    return None


# ---------------------------------------------------------------------------
# Pricing constants (Opus 4.8 via Batch API)
# ---------------------------------------------------------------------------

_PRICING_INPUT_PER_MTOK: float = 5.0
"""USD per million input tokens (Opus 4.8 standard rate)."""

_PRICING_OUTPUT_PER_MTOK: float = 25.0
"""USD per million output tokens (Opus 4.8 standard rate)."""

_BATCH_DISCOUNT: float = 0.5
"""Batch API discount — 50% off standard rate."""

_ESTIMATED_OUTPUT_TOKENS_PER_REQUEST: int = 100
"""Conservative output estimate for dry-run cost projection."""

_BATCH_POLL_INTERVAL_SEC: float = 60.0
"""Seconds between Batch API status polls."""

PROMPT_VERSION: str = "v1"
"""System prompt version — changing this invalidates disk cache (D3).

Increment when the system prompt text changes so that cached classifications
built against an old prompt are not served for new queries.
"""

# ---------------------------------------------------------------------------
# Classification JSON schema (D6 — structured outputs, AR R5)
# ---------------------------------------------------------------------------

_CLASSIFICATION_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "target": {
            "type": "string",
            "enum": ["PRODUCT", "TEST", "CONFIG", "DOCS", "OTHER"],
        },
        "origin": {
            "type": "string",
            "enum": ["Code", "Design", "Integration", "Environment", "Requirements"],
        },
        "bug_type": {
            "type": "string",
            "enum": ["Logic", "State", "Interface", "Performance", "Security"],
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 0.99},
        "rationale": {"type": "string"},
    },
    "required": ["target", "origin", "bug_type", "confidence", "rationale"],
    "additionalProperties": False,
}
"""JSON schema for structured LLM output (output_config.format.json_schema).

Guarantees parse-safe responses on both Batch and single Messages API calls.
The schema enumerates valid values for target/origin/bug_type to eliminate
fence-stripping and manual parse recovery (D6 compliance).
"""

# ---------------------------------------------------------------------------
# System prompt (from spike — target/origin/bug_type definitions)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = f"""You are a software quality analyst classifying escaped bugs.
Given a bug title, description, unified diff, and commit message, classify the change.

## Output format
Respond with ONLY a JSON object (no markdown, no prose):
{{
  "target": "<PRODUCT|TEST|CONFIG|DOCS|OTHER>",
  "origin": "<Code|Design|Integration|Environment|Requirements>",
  "bug_type": "<Logic|State|Interface|Performance|Security>",
  "confidence": <float between 0.0 and 0.99>,
  "rationale": "<1-2 sentence explanation>"
}}

## Target definitions
- PRODUCT: change touches production source code that ships to users
- TEST: change only touches test files, fixtures, or test infra
- CONFIG: change only touches CI/CD, environment config, build config, or CVE pins
- DOCS: change only touches documentation, comments, or README
- OTHER: change does not fit the above (e.g. tooling, migration scripts)

**CRITICAL: Design vs Code origin**
Design bugs are failures in architecture or system design — not implementation typos.
A wrong data model, incorrect API contract, or missing abstraction = Design.
A wrong variable value, off-by-one, or incorrect algorithm = Code.
Regex and keyword heuristics systematically mis-classify Design as Code — do not.

## Origin definitions (cf13269)
- Code: implementation error (wrong logic, off-by-one, type error)
- Design: architectural or design decision error (wrong model, bad API contract)
- Integration: two correct components interact incorrectly
- Environment: infrastructure, dependency, or configuration issue
- Requirements: misunderstood or missing requirements

## Bug type definitions (cf13267)
- Logic: incorrect program logic
- State: incorrect state management or side-effects
- Interface: incorrect API, contract, or interface definition
- Performance: throughput, latency, or resource-usage issue
- Security: CVE, auth, or permission issue

## CVE rule
Any change that pins a dependency to fix a CVE → target=CONFIG, origin=Environment.

## Confidence
0.99 maximum. Use < 0.6 when signals are insufficient or contradictory.
prompt_version: {PROMPT_VERSION}
"""

# ---------------------------------------------------------------------------
# LlmProvider Protocol — BYOK seam (RAISE-11585)
# ---------------------------------------------------------------------------


@runtime_checkable
class LlmProvider(Protocol):
    """Protocol for LLM classification — BYOK seam (RAISE-11585).

    Design constraints:
    - Two methods: classify_single_raw (sync, low-latency) and classify_batch_raw
      (Batch API, bulk economy). Both required to separate the single-call path
      from the async batch path (AR R2).
    - Structural typing: adding OpenRouterProvider requires ONLY implementing
      these two methods — no changes to TargetClassifier, ClassifierConfig, or
      this protocol definition.
    - @runtime_checkable: enables isinstance() checks in tests (belt-and-suspenders
      alongside Pyright structural check).
    """

    def classify_single_raw(
        self,
        request: dict[str, object],
        *,
        model: str,
    ) -> dict[str, object]:
        """Submit a single classification request synchronously (AR R2).

        Used by classify() for interactive/single-bug callers. Avoids the
        Batch API polling delay (minutes–24h) for one-shot calls.

        Args:
            request: Dict with:
                - "custom_id": str — unique identifier
                - "prompt": str — user-turn classification prompt (no system prompt)
            model: Claude model ID (e.g. "claude-opus-4-8").

        Returns:
            Dict with:
            - "custom_id": str — echoes input custom_id
            - "result": str — raw JSON text from the LLM
        """
        ...

    def classify_batch_raw(
        self,
        requests: list[dict[str, object]],
        *,
        model: str,
        dry_run: bool = False,
    ) -> list[dict[str, object]]:
        """Submit a batch of classification requests and return raw results.

        Args:
            requests: List of request dicts, each with:
                - "custom_id": str — unique identifier (maps results back to bugs)
                - "prompt": str — user-turn classification prompt (no system prompt)
            model: Claude model ID (e.g. "claude-opus-4-8").
            dry_run: When True, estimate cost without making real API calls.
                Returns a list with a single CostEstimate-shaped dict.

        Returns:
            List of result dicts, each with:
            - "custom_id": str — matches input custom_id
            - "result": str — raw JSON text (or CostEstimate fields for dry_run)
            - "errored": bool — True for transient failures (AR R4: must NOT be cached)

        Note: Results are mapped by custom_id, NEVER by position.
        """
        ...


# ---------------------------------------------------------------------------
# AnthropicProvider — T3 full implementation
# ---------------------------------------------------------------------------


class AnthropicProvider:
    """Anthropic SDK implementation of LlmProvider.

    Uses the Batch API for backfill economy (-50% vs. standard Messages API).
    Lazy-imports ``anthropic`` so raise-cli works without it installed.

    API patterns:
    - Batch submit: ``client.messages.batches.create(requests=[...])``
    - Poll until ``batch.processing_status == "ended"``
    - Results: ``client.messages.batches.results(batch.id)`` — mapped by custom_id
    - Dry-run: ``client.messages.count_tokens(model=..., messages=[...])``
    - Thinking: ``thinking={"type": "adaptive"}`` — no budget_tokens, no temperature
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Initialise provider with optional explicit API key.

        The key is stored and passed to the Anthropic client at call time.
        None means the SDK will use ANTHROPIC_API_KEY from the environment.
        """
        self._api_key = api_key

    def classify_single_raw(
        self,
        request: dict[str, object],
        *,
        model: str,
    ) -> dict[str, object]:
        """Submit a single classification request via synchronous Messages API (AR R2).

        Uses ``client.messages.create`` (not Batch API) — no polling delay.
        System prompt sent with prompt caching to amortise its stable cost (AR R1).
        Structured output via output_config.format.json_schema (AR R5).

        Args:
            request: Dict with ``custom_id`` and ``prompt`` (user-turn only).
            model: Claude model ID.

        Returns:
            Dict with ``custom_id`` and ``result`` (raw JSON text).
        """
        import anthropic  # noqa: PLC0415 — lazy import; intentional

        client = anthropic.Anthropic(api_key=self._api_key)
        user_prompt = str(request.get("prompt", ""))

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": _CLASSIFICATION_SCHEMA,
                }
            },
        )

        text = next(
            (block.text for block in response.content if block.type == "text"),
            "",
        )
        return {
            "custom_id": str(request.get("custom_id", "")),
            "result": text,
        }

    def classify_batch_raw(
        self,
        requests: list[dict[str, object]],
        *,
        model: str,
        dry_run: bool = False,
    ) -> list[dict[str, object]]:
        """Submit batch to Anthropic API and return raw results.

        Args:
            requests: Request dicts with ``custom_id`` and ``prompt`` keys
                (user-turn only — system prompt is sent via ``params.system``).
            model: Claude model ID.
            dry_run: When True, estimate cost via count_tokens without batching.

        Returns:
            - dry_run=False: list of ``{"custom_id": str, "result": str,
              "errored": bool}`` dicts in the same order as input requests.
            - dry_run=True: single-element list with a CostEstimate-shaped dict.
        """
        import anthropic  # noqa: PLC0415 — lazy import; intentional

        client = anthropic.Anthropic(api_key=self._api_key)

        if dry_run:
            return self._dry_run(client, requests, model)
        return self._submit_batch(client, requests, model)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _dry_run(
        self,
        client: object,
        requests: list[dict[str, object]],
        model: str,
    ) -> list[dict[str, object]]:
        """Estimate cost via count_tokens without making real batch API calls."""
        total_input_tokens = 0
        for req in requests:
            prompt = str(req.get("prompt", ""))
            resp = client.messages.count_tokens(  # type: ignore[union-attr]
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            total_input_tokens += resp.input_tokens

        total_output_tokens = len(requests) * _ESTIMATED_OUTPUT_TOKENS_PER_REQUEST

        input_cost = total_input_tokens / 1_000_000 * _PRICING_INPUT_PER_MTOK
        output_cost = total_output_tokens / 1_000_000 * _PRICING_OUTPUT_PER_MTOK
        estimated_usd = (input_cost + output_cost) * _BATCH_DISCOUNT

        return [
            {
                "bug_count": len(requests),
                "estimated_input_tokens": total_input_tokens,
                "estimated_output_tokens": total_output_tokens,
                "estimated_usd": estimated_usd,
                "model": model,
                "cache_hits": 0,
            }
        ]

    def _submit_batch(
        self,
        client: object,
        requests: list[dict[str, object]],
        model: str,
    ) -> list[dict[str, object]]:
        """Submit to Batch API, poll until complete, map results by custom_id.

        Uses plain dicts for batch request construction — avoids sub-package
        imports that break under sys.modules patching in tests. The SDK accepts
        dict-shaped requests identical to the typed Request objects.

        Fixes (AR):
        - R1: system prompt sent via ``params.system`` with ``cache_control``
          (not embedded in user content) — avoids re-charging the stable prefix
          per bug across ~526 backfill calls.
        - Q2/R5: max_tokens raised to 1024; output_config.format.json_schema
          guarantees parse-safe structured output.
        - R4: errored items marked with ``"errored": True`` so callers can skip
          caching transient failures.

        Note: ``anthropic`` is imported lazily in ``classify_batch_raw`` — no
        re-import needed here since this helper is always called from that method.
        """
        batch_requests = [
            {
                "custom_id": str(req["custom_id"]),
                "params": {
                    "model": model,
                    "max_tokens": 1024,
                    "thinking": {"type": "adaptive"},
                    "system": [
                        {
                            "type": "text",
                            "text": _SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    "messages": [
                        {"role": "user", "content": str(req.get("prompt", ""))}
                    ],
                    "output_config": {
                        "format": {
                            "type": "json_schema",
                            "schema": _CLASSIFICATION_SCHEMA,
                        }
                    },
                },
            }
            for req in requests
        ]

        batch = client.messages.batches.create(requests=batch_requests)  # type: ignore[union-attr]

        # Poll until processing is complete
        while batch.processing_status != "ended":
            time.sleep(_BATCH_POLL_INTERVAL_SEC)
            batch = client.messages.batches.retrieve(batch.id)  # type: ignore[union-attr]

        # Build a map custom_id → {result, errored} (NEVER use positional indexing)
        result_map: dict[str, dict[str, object]] = {}
        for item in client.messages.batches.results(batch.id):  # type: ignore[union-attr]
            if item.result.type == "succeeded":
                text = next(
                    (
                        block.text
                        for block in item.result.message.content
                        if block.type == "text"
                    ),
                    "",
                )
                result_map[item.custom_id] = {"result": text, "errored": False}
            else:
                # R4: mark as errored — caller must NOT cache this
                result_map[item.custom_id] = {"result": "", "errored": True}

        # Return in INPUT order, mapped by custom_id
        return [
            {
                "custom_id": str(req["custom_id"]),
                "result": result_map.get(str(req["custom_id"]), {}).get("result", ""),
                "errored": result_map.get(str(req["custom_id"]), {"errored": True}).get(
                    "errored", True
                ),
            }
            for req in requests
        ]


# ---------------------------------------------------------------------------
# TargetClassifier — T4 skeleton (classify() full impl in T5)
# ---------------------------------------------------------------------------


class TargetClassifier:
    """LLM-backed target/origin/bug_type classifier.

    Complements ``target_from_paths`` (S11487.2):
    - ``target_from_paths`` → cheap, deterministic, requires diff paths
    - ``TargetClassifier.classify`` → LLM, reads bug+diff+commit, infers
      origin/bug_type and resolves ambiguous targets

    Graceful degradation (D5):
    - No API key → paths-only fallback; origin/bug_type = "unknown"; no crash
    - Low confidence → target=UNKNOWN, confidence=0.0, explicit rationale

    BYOK seam (RAISE-11585):
    - provider slot typed as ``LlmProvider`` protocol — adding OpenRouterProvider
      is purely additive (no TargetClassifier refactor required)
    """

    def __init__(
        self,
        config: ClassifierConfig | None = None,
        *,
        hermes_path: str = _DEFAULT_HERMES_PATH,
        provider: LlmProvider | None = None,
    ) -> None:
        """Initialise the classifier.

        Args:
            config: Classifier configuration. Defaults to ``ClassifierConfig()``.
            hermes_path: Path to hermes auth.json for credential resolution.
                Overrideable in tests (default: ``~/.hermes/auth.json``).
            provider: Injected ``LlmProvider`` implementation (AR Q1 — BYOK seam).
                When provided, credential resolution is skipped entirely.
                Enables testing without AnthropicProvider and BYOK for RAISE-11585.
        """
        from raise_cli.reliability.classification_models import (
            ClassifierConfig,  # noqa: PLC0415
        )

        self._config = config or ClassifierConfig()
        self._hermes_path = hermes_path

        if provider is not None:
            # Injected provider takes precedence — skip credential resolution (AR Q1)
            self._provider: LlmProvider | None = provider
        else:
            # Resolve credential — None means degraded mode (no provider instantiated)
            api_key = _resolve_credential(self._config, hermes_path=hermes_path)
            if api_key is not None:
                self._provider = AnthropicProvider(api_key=api_key)
            else:
                self._provider = None

    def classify(
        self,
        bug: BugRecord,
        fix_diff: str = "",
        commit: str = "",
    ) -> TargetClassification:
        """Classify a single bug.

        When no provider is available (no API key), degrades to paths-only
        fallback: target is derived from the diff paths, origin/bug_type = "unknown",
        confidence = 0.0, rationale explains the fallback.

        Full LLM implementation in Task 5. This T4 skeleton handles the
        degradation path only.

        Args:
            bug: Bug record with key, title, description.
            fix_diff: Unified diff string for the fix commit.
            commit: Commit SHA or message string.

        Returns:
            TargetClassification with all fields populated.
        """
        from raise_cli.reliability.classification_models import (
            TargetClassification,  # noqa: PLC0415
        )
        from raise_cli.reliability.targets import target_from_paths  # noqa: PLC0415

        if self._provider is None:
            # Graceful degradation (D5): no LLM available — paths-only fallback
            paths = _extract_paths_from_diff(fix_diff)
            from raise_cli.reliability.models import Target  # noqa: PLC0415

            fallback_target = target_from_paths(paths) if paths else Target.UNKNOWN
            return TargetClassification(
                bug_key=bug.key,
                target=fallback_target,
                origin="unknown",
                bug_type="unknown",
                confidence=0.0,
                rationale="no LLM provider configured — paths-only fallback",
            )

        # Full LLM classify path: synchronous single call (AR R2 — not Batch API).
        # Batch API has minutes–24h latency; single classify() calls expect
        # interactive latency. Reserve Batch for classify_batch() backfill.
        user_prompt = _build_user_prompt(bug, fix_diff, commit)
        raw_result = self._provider.classify_single_raw(
            {"custom_id": bug.key, "prompt": user_prompt},
            model=self._config.model,
        )
        raw_text = str(raw_result.get("result", ""))
        return _parse_response(raw_text, bug.key, self._config)

    def classify_batch(
        self,
        bugs: list[BugRecord],
        *,
        fix_diff: str = "",
        commit: str = "",
        batch_size: int | None = None,
        dry_run: bool = False,
    ) -> list[TargetClassification] | CostEstimate:
        """Classify multiple bugs, with disk caching and dry-run support.

        Args:
            bugs: List of bugs to classify.
            fix_diff: Shared unified diff (applied to all bugs). For per-bug diffs,
                call classify() individually.
            commit: Shared commit SHA or message.
            batch_size: Overrides config.batch_size if provided.
            dry_run: When True, estimate cost without API calls. Returns CostEstimate.

        Returns:
            - dry_run=False: list of TargetClassification (one per bug, in input order)
            - dry_run=True: CostEstimate for the full batch
        """
        from raise_cli.reliability.classification_models import (  # noqa: PLC0415
            CostEstimate,
        )

        bsz = batch_size or self._config.batch_size

        if dry_run:
            # Build requests for all bugs (no cache check in dry-run)
            dry_requests: list[dict[str, object]] = [
                {
                    "custom_id": bug.key,
                    "prompt": _build_user_prompt(bug, fix_diff, commit),
                }
                for bug in bugs
            ]
            if self._provider is None or not dry_requests:
                return CostEstimate(
                    bug_count=len(bugs),
                    estimated_input_tokens=0,
                    estimated_output_tokens=0,
                    estimated_usd=0.0,
                    model=self._config.model,
                    cache_hits=0,
                )
            raw = self._provider.classify_batch_raw(
                dry_requests, model=self._config.model, dry_run=True
            )
            est_data: dict[str, object] = raw[0] if raw else {}
            return CostEstimate(
                bug_count=int(est_data.get("bug_count", len(bugs))),  # type: ignore[arg-type]
                estimated_input_tokens=int(est_data.get("estimated_input_tokens", 0)),  # type: ignore[arg-type]
                estimated_output_tokens=int(est_data.get("estimated_output_tokens", 0)),  # type: ignore[arg-type]
                estimated_usd=float(est_data.get("estimated_usd", 0.0)),  # type: ignore[arg-type]
                model=str(est_data.get("model", self._config.model)),
                cache_hits=0,
            )

        # Non-dry-run: check cache first, only call provider for misses
        results: list[TargetClassification] = []
        diff_hash = _sha256_hex(fix_diff)

        cache_hits = 0
        misses: list[tuple[int, BugRecord]] = []  # (original_index, bug)

        for idx, bug in enumerate(bugs):
            cached = _load_cache(bug.key, diff_hash, commit, self._config)
            if cached is not None:
                results.append(cached)
                cache_hits += 1
            else:
                results.append(None)  # type: ignore[arg-type]  # placeholder
                misses.append((idx, bug))

        # Process misses in batches
        for batch_start in range(0, len(misses), bsz):
            batch = misses[batch_start : batch_start + bsz]
            if not batch:
                continue

            if self._provider is None:
                # Degraded mode: fill with fallback classifications
                for idx, bug in batch:
                    results[idx] = self.classify(bug, fix_diff=fix_diff, commit=commit)
                continue

            self._process_miss_batch(batch, fix_diff, commit, diff_hash, results)

        return results  # type: ignore[return-value]

    def _process_miss_batch(
        self,
        batch: list[tuple[int, BugRecord]],
        fix_diff: str,
        commit: str,
        diff_hash: str,
        results: list[TargetClassification],
    ) -> None:
        """Process one batch of cache-miss bugs through the LLM provider.

        Mutates ``results`` in-place at the original bug indices.
        Only caches results that are NOT transient failures (AR R4).

        Args:
            batch: List of (original_index, bug) pairs.
            fix_diff: Shared diff string for prompt building.
            commit: Commit string for prompt building.
            diff_hash: SHA-256 of fix_diff (pre-computed for cache key).
            results: Mutable list to write classifications into.
        """
        batch_requests: list[dict[str, object]] = [
            {
                "custom_id": bug.key,
                "prompt": _build_user_prompt(bug, fix_diff, commit),
            }
            for _, bug in batch
        ]
        raw_results = self._provider.classify_batch_raw(  # type: ignore[union-attr]
            batch_requests, model=self._config.model, dry_run=False
        )
        # Store full result dicts keyed by custom_id (R4: need errored flag)
        raw_map: dict[str, dict[str, object]] = {
            str(r.get("custom_id", "")): r for r in raw_results
        }
        for idx, bug in batch:
            raw_data = raw_map.get(bug.key, {})
            raw_text = str(raw_data.get("result", ""))
            errored = bool(raw_data.get("errored", False))
            classification = _parse_response(raw_text, bug.key, self._config)
            results[idx] = classification
            # R4: only cache genuine classifications — skip transient failures
            if not errored:
                _save_cache(bug.key, diff_hash, commit, self._config, classification)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_user_prompt(bug: BugRecord, fix_diff: str, commit: str) -> str:
    """Build the user-turn classification prompt for a single bug.

    The system prompt (``_SYSTEM_PROMPT``) is sent via the API ``system``
    parameter with ``cache_control: {"type": "ephemeral"}`` — NOT embedded
    here (AR R1: avoids re-charging the stable ~80-line prefix per bug).

    ``PROMPT_VERSION`` is baked into ``_SYSTEM_PROMPT`` for cache invalidation.

    Args:
        bug: Bug record with key, title, description.
        fix_diff: Unified diff string (may be empty).
        commit: Commit SHA or message string.

    Returns:
        User-turn prompt containing only bug/diff/commit context (no system prefix).
    """
    diff_section = (
        f"## Diff\n```\n{fix_diff}\n```" if fix_diff else "## Diff\n(no diff available)"
    )
    desc_section = (
        f"**Description:** {bug.description}" if bug.description else "(no description)"
    )
    return (
        f"## Bug to classify\n"
        f"**Key:** {bug.key}\n"
        f"**Title:** {bug.title}\n"
        f"{desc_section}\n\n"
        f"{diff_section}\n\n"
        f"## Commit message\n{commit or '(no commit message)'}\n"
    )


def _parse_response(
    raw: str,
    bug_key: str,
    config: ClassifierConfig,
) -> TargetClassification:
    """Parse a raw classification response into TargetClassification.

    Applies the confidence gate: if the parsed confidence ≤ threshold,
    returns Target.UNKNOWN with confidence=0.0 (D5 — no invented classification).

    Args:
        raw: Raw JSON string from the LLM (may be malformed).
        bug_key: Bug key for the TargetClassification.
        config: ClassifierConfig (for threshold, model).

    Returns:
        TargetClassification with all fields populated.
        Falls back to UNKNOWN with confidence=0.0 on any parse error.
    """
    import json  # noqa: PLC0415

    from raise_cli.reliability.classification_models import (
        TargetClassification,  # noqa: PLC0415
    )
    from raise_cli.reliability.models import Target  # noqa: PLC0415

    def _unknown(rationale: str) -> TargetClassification:
        return TargetClassification(
            bug_key=bug_key,
            target=Target.UNKNOWN,
            origin="unknown",
            bug_type="unknown",
            confidence=0.0,
            rationale=rationale,
        )

    try:
        # With output_config.format.json_schema, response is guaranteed valid JSON.
        # No fence stripping needed (AR R5 — structured outputs replace heuristics).
        data = json.loads(raw.strip())
    except (json.JSONDecodeError, ValueError):
        return _unknown(f"parse error — could not decode JSON response: {raw[:100]!r}")

    raw_confidence = float(data.get("confidence", 0.0))
    # Never exactly 1.0 (Field lt=1.0) — clamp to 0.99 if needed
    confidence = min(raw_confidence, 0.99)

    # Confidence gate (D5): below threshold → UNKNOWN
    if confidence <= config.confidence_threshold:
        return _unknown(
            f"confidence {confidence:.2f} below threshold {config.confidence_threshold:.2f}"
        )

    raw_target = str(data.get("target", "unknown")).lower()
    try:
        target = Target(raw_target)
    except ValueError:
        return _unknown(f"unknown target value: {raw_target!r}")

    return TargetClassification(
        bug_key=bug_key,
        target=target,
        origin=str(data.get("origin", "unknown")),
        bug_type=str(data.get("bug_type", "unknown")),
        confidence=confidence,
        rationale=str(data.get("rationale", "")),
    )


def _extract_paths_from_diff(diff: str) -> list[str]:
    """Extract changed file paths from a unified diff string.

    Parses ``--- a/path`` and ``+++ b/path`` lines. Returns unique paths,
    excluding /dev/null (new-file/deleted-file markers).
    """
    paths: list[str] = []
    for line in diff.splitlines():
        if line.startswith("--- a/") or line.startswith("+++ b/"):
            path = line[6:]  # strip "--- a/" or "+++ b/"
            if path != "/dev/null" and path not in paths:
                paths.append(path)
    return paths


def _sha256_hex(text: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 string."""
    import hashlib  # noqa: PLC0415

    return hashlib.sha256(text.encode()).hexdigest()


def _cache_key(
    bug_key: str, diff_hash: str, commit: str, config: ClassifierConfig
) -> str:
    """Build the disk cache key.

    Cache key = sha256(bug_key + diff_hash + commit_sha + model + PROMPT_VERSION)
    Changing any component (especially PROMPT_VERSION) invalidates the cache.
    """
    raw = f"{bug_key}:{diff_hash}:{commit}:{config.model}:{PROMPT_VERSION}"
    return _sha256_hex(raw)


def _load_cache(
    bug_key: str,
    diff_hash: str,
    commit: str,
    config: ClassifierConfig,
) -> TargetClassification | None:
    """Load a cached classification from disk. Returns None on cache miss or error."""
    if config.cache_dir is None:
        return None

    from raise_cli.reliability.classification_models import (
        TargetClassification,  # noqa: PLC0415
    )

    cache_dir = Path(config.cache_dir) / "target_classifier"
    key = _cache_key(bug_key, diff_hash, commit, config)
    cache_file = cache_dir / f"{key}.json"

    if not cache_file.is_file():
        return None

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        return TargetClassification.model_validate(data)
    except Exception:  # noqa: BLE001
        return None  # Corrupted cache → treat as miss


def _save_cache(
    bug_key: str,
    diff_hash: str,
    commit: str,
    config: ClassifierConfig,
    classification: TargetClassification,
) -> None:
    """Write a classification to the disk cache. Failures are silently swallowed."""
    if config.cache_dir is None:
        return

    cache_dir = Path(config.cache_dir) / "target_classifier"
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        key = _cache_key(bug_key, diff_hash, commit, config)
        cache_file = cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps(classification.model_dump()), encoding="utf-8")
    except OSError:
        pass  # Cache write failure is non-fatal


if TYPE_CHECKING:
    from raise_cli.reliability.classification_models import (
        BugRecord,
        ClassifierConfig,
        CostEstimate,
        TargetClassification,
    )
