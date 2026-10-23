"""LLM-powered semantic turn classifier for post-session distillation.

Replaces regex heuristics with Haiku 4.5 batch classification (100 turns/call).
Falls back to the heuristic classifier per chunk on API failure.

Architecture:
  - classify_turns_llm(records) → list[TurnClass]
  - Chunks of CHUNK_SIZE turns, each sent as one structured-output call
  - On LLM failure per chunk: fall back to classify_turn() for that chunk
  - TOOL_USE is NOT classified by LLM — it is a structural property (has_tools)

Auth strategy:
  - Primary: Anthropic SDK (requires ANTHROPIC_API_KEY env var)
  - Fallback: `claude -p` subprocess (works in OAuth/Claude Code environments)
  - Final fallback: heuristic classifier
"""

from __future__ import annotations

import json
import logging
import os
import subprocess

from pydantic import BaseModel

from raise_cli.distillation.classifier import (
    TurnClass,
    classify_structural,
    classify_turn,
)
from raise_cli.distillation.parser import TurnRecord
from raise_cli.distillation.segment import Segment

logger = logging.getLogger(__name__)

CHUNK_SIZE = 100
# DeepSeek V4 Flash silently truncates json_object responses over ~600 chars.
# Reduced from 50→10 (SOTA research: batch >10 degrades classification quality,
# arXiv:2406.10786). Confidence scores in response also reduce per-item length.
_DEEPSEEK_CHUNK_SIZE = 10
_MODEL = "claude-haiku-4-5-20251001"
_DEEPSEEK_MODEL = "deepseek-v4-flash"

# Available classifier backends (passed via --backend or RAISE_DISTILLATION_BACKEND env var)
BACKENDS = ("anthropic", "deepseek", "openrouter", "subprocess")

# Shared durability criteria used in both the per-turn classifier and the episodic
# extractor prompts (D5). Keep in sync with the inline text in _SYSTEM_PROMPT and
# _COT_SYSTEM_PROMPT if those prompts are updated independently.
_DURABILITY_CRITERIA = """\
POSITIVE — must satisfy at least ONE:
  • Identifies a recurring pattern or systemic behavior (not a one-time event)
  • Explains WHY something failed or worked (root cause, not just description)
  • Establishes a rule or principle applicable in future sessions or projects
  • Names a design risk, contract break, or silent assumption
  • Discovers dead code, orphaned artifacts, or a concrete gap/limitation

EXCLUSION — not an insight if ANY applies:
  • Progress narration: "I did X", "I finished Y", "Spawning agent", "Let me check"
  • Commit/MR/branch/Jira status: "MR !679 merged", "RAISE-X cerrado", "branch limpio"
  • Implementation description without a finding: just describing what was built
  • Operational instruction relevant only to this moment: "you need to run X now"
  • Confirmation that something works, without explaining why or what the principle is

DURABILITY TEST: Would this be valuable to a developer on a DIFFERENT project, 6 months later?
  If NO → not an insight. If YES and at least one positive criterion is met → insight.\
"""

_SYSTEM_PROMPT = """\
You are a turn classifier for software engineering session transcripts.
Each turn is prefixed with its role: "user:" (developer) or "assistant:" (AI).

Classify each turn into EXACTLY ONE of these classes:

- decision: a "user:" turn where the developer approves, confirms, or authorizes.
  Includes: "ok adelante", "sí", "approved", "go ahead", "confirmed", "correct".
  Also includes HITL answer injections starting with "Your questions have been answered:".
  Also includes short tool-use approvals and any affirmative developer response.
  NEVER apply to "assistant:" turns.

- correction: a "user:" turn where the developer rejects, corrects, or reverts.
  Includes: "no that's wrong", "revert that", tool-rejection injections
  ("The user doesn't want to proceed with this tool use..."), "eso está mal", "fix it".
  NEVER apply to "assistant:" turns.

- insight: an "assistant:" turn satisfying ALL of:
  POSITIVE — must have at least one:
    • Identifies a recurring pattern or systemic behavior (not a one-time event)
    • Explains WHY something failed or worked (root cause, not just description)
    • Establishes a rule or principle applicable in future sessions or projects
    • Names a design risk, contract break, or silent assumption
    • Discovers dead code, orphaned artifacts, or a concrete gap/limitation
  EXCLUSION — classify as neutral if any of these apply:
    • Progress narration: "I did X", "I finished Y", "Spawning agent", "Let me check"
    • Commit/MR/branch/Jira status: "MR !679 merged", "RAISE-X cerrado", "branch limpio"
    • Implementation description without a finding: just describing what was built
    • Operational instruction relevant only to this moment: "you need to run X now"
    • Confirmation that something works, without explaining why or what the principle is
  DURABILITY TEST: Would this be valuable to a developer on a DIFFERENT project, 6 months later?
    If NO → neutral. If YES and the positive criteria are met → insight.
  NEVER apply to "user:" turns.

- blocker: a STOP signal or hard blocker from either party
  (e.g. "STOP —", "blocked:", "blocked —")

- neutral: everything else — questions, context, status updates, tool results,
  AND ALL assistant pipeline narration regardless of content

NEVER classify as decision or correction:
- Harness-injected XML: <task-notification>, <system-reminder>, <antml-thinking> blocks
- Tool output or JSON success responses ({"success": true, ...})
- Background task completion messages

Rules:
- Assign only ONE class per turn
- "assistant:" turns are NEVER decision or correction
- "user:" turns are NEVER insight
- Default to neutral when uncertain — insight is rare (~5-8% of assistant turns)

Output format: {"classifications": [{"index": 0, "class": "decision", "confidence": 3}, ...]}
Confidence is 1 (very uncertain) to 5 (very certain). Include for every entry.
"""

_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "class": {
                        "type": "string",
                        "enum": [
                            "decision",
                            "correction",
                            "insight",
                            "blocker",
                            "neutral",
                        ],
                    },
                    "confidence": {"type": "integer", "minimum": 1, "maximum": 5},
                },
                "required": ["index", "class", "confidence"],
            },
        }
    },
    "required": ["classifications"],
}

_CLASS_MAP: dict[str, TurnClass] = {
    "decision": TurnClass.DECISION,
    "correction": TurnClass.CORRECTION,
    "insight": TurnClass.INSIGHT,
    "blocker": TurnClass.BLOCKER,
    "neutral": TurnClass.NEUTRAL,
}


def _build_chunk_prompt(records: list[TurnRecord], start_index: int) -> str:
    """Build the user-turn text for a classification chunk."""
    lines = []
    for i, rec in enumerate(records):
        snippet = rec.content_text[:500].replace("\n", " ")
        lines.append(f"[{start_index + i}] {rec.turn_type.value}: {snippet}")
    return "\n".join(lines)


def _parse_chunk_response(
    text: str, records: list[TurnRecord], start_index: int
) -> list[tuple[TurnClass, int]] | None:
    """Parse JSON classification response into (TurnClass, confidence) pairs."""
    try:
        data = json.loads(text)
        by_index: dict[int, tuple[str, int]] = {
            item["index"]: (item["class"], int(item.get("confidence", 3)))
            for item in data["classifications"]
        }
        result: list[tuple[TurnClass, int]] = []
        for i, _ in enumerate(records):
            cls_str, confidence = by_index.get(start_index + i, ("neutral", 3))
            result.append((_CLASS_MAP.get(cls_str, TurnClass.NEUTRAL), confidence))
        return result
    except (json.JSONDecodeError, KeyError) as exc:
        logger.warning("LLM classifier JSON parse failed: %s — raw: %.200s", exc, text)
        return None


def _classify_chunk_anthropic(
    records: list[TurnRecord],
    client: object,
    start_index: int,
) -> list[tuple[TurnClass, int]] | None:
    """Classify via Anthropic SDK (Haiku 4.5, structured output)."""
    user_text = _build_chunk_prompt(records, start_index)
    try:
        response = client.messages.create(  # type: ignore[attr-defined]
            model=_MODEL,
            max_tokens=8192,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_text}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": _OUTPUT_SCHEMA,
                    "name": "turn_classifications",
                }
            },
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        return _parse_chunk_response(text, records, start_index)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Anthropic classifier failed: %s", exc)
        return None


def _classify_chunk_llm(
    records: list[TurnRecord],
    client: object,
    start_index: int,
    *,
    backend: str = "deepseek",
) -> list[tuple[TurnClass, int]] | None:
    """Dispatch to the selected backend — no implicit fallback chain."""
    if backend == "anthropic":
        return _classify_chunk_anthropic(records, client, start_index)
    if backend == "deepseek":
        return _classify_chunk_deepseek(records, start_index)
    if backend == "openrouter":
        or_model = os.environ.get("OPENROUTER_MODEL", "moonshotai/kimi-k2")
        return _classify_chunk_openrouter(records, start_index, model=or_model)
    if backend == "subprocess":
        return _classify_chunk_subprocess(records, start_index)
    raise ValueError(f"Unknown classifier backend {backend!r}. Choose: {BACKENDS}")


def _extract_first_json_object(text: str) -> str:
    """Extract the first complete JSON object from text that may have trailing content."""
    brace = text.find("{")
    if brace == -1:
        return text
    depth = 0
    for i, ch in enumerate(text[brace:], brace):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[brace : i + 1]
    return text[brace:]


def _openrouter_classify(
    records: list[TurnRecord],
    start_index: int,
    *,
    model: str,
    api_key: str,
) -> list[tuple[TurnClass, int]] | None:
    """Classify via any OpenAI-compatible API (DeepSeek, OpenRouter, etc.)."""
    import openai

    base_url = (
        "https://api.deepseek.com"
        if "deepseek" in model
        else "https://openrouter.ai/api/v1"
    )
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    user_text = _build_chunk_prompt(records, start_index)
    n = len(records)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"{user_text}\n\n"
                    f"Return ONLY a JSON object with key 'classifications' containing "
                    f"an array of exactly {n} objects (one per turn above), "
                    f"each with 'index' (integer) and 'class' (string). "
                    "No explanation, no markdown fences."
                ),
            },
        ],
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    text = response.choices[0].message.content or ""
    return _parse_chunk_response(_extract_first_json_object(text), records, start_index)


def _classify_chunk_deepseek(
    records: list[TurnRecord],
    start_index: int,
) -> list[tuple[TurnClass, int]] | None:
    """Classify via DeepSeek API (V4 Flash)."""
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    if not deepseek_key:
        logger.warning("DEEPSEEK_API_KEY not set — deepseek backend unavailable")
        return None
    try:
        return _openrouter_classify(
            records, start_index, model=_DEEPSEEK_MODEL, api_key=deepseek_key
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("DeepSeek classifier failed: %s", exc)
        return None


def _classify_chunk_openrouter(
    records: list[TurnRecord],
    start_index: int,
    *,
    model: str = "moonshotai/kimi-k2",
) -> list[tuple[TurnClass, int]] | None:
    """Classify via OpenRouter (Kimi K2/K3 or any hosted model)."""
    or_key = os.environ.get("OPENROUTER_API_KEY")
    if not or_key:
        return None
    try:
        return _openrouter_classify(records, start_index, model=model, api_key=or_key)
    except Exception as exc:  # noqa: BLE001
        logger.warning("OpenRouter classifier (%s) failed: %s", model, exc)
        return None


def _classify_chunk_subprocess(
    records: list[TurnRecord],
    start_index: int,
) -> list[tuple[TurnClass, int]] | None:
    """Classify via `claude -p` subprocess — last resort, OAuth environments only."""
    user_text = _build_chunk_prompt(records, start_index)
    prompt = (
        f"{_SYSTEM_PROMPT}\n\nTurns to classify:\n{user_text}\n\n"
        "Return ONLY the JSON object, no other text:\n"
        '{"classifications": [{"index": N, "class": "..."}]}'
    )
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", _MODEL],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if proc.returncode != 0:
            logger.warning("subprocess classifier failed: %s", proc.stderr[:200])
            return None
        text = proc.stdout.strip()
        return _parse_chunk_response(
            _extract_first_json_object(text), records, start_index
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        logger.warning("subprocess classifier error: %s", exc)
        return None


def _classify_chunk(
    chunk: list[TurnRecord],
    client: object,
    chunk_start: int,
    *,
    backend: str = "deepseek",
) -> list[tuple[TurnClass, int]]:
    """Classify one chunk: structural pre-pass then LLM, with heuristic fallback.

    Returns (TurnClass, confidence) pairs. Structural pre-pass turns get confidence=5.
    Heuristic fallback INSIGHT turns get confidence=3 (mid-range, no LLM signal).

    Privacy gate: developer turns (is_developer=True) are never sent to the LLM —
    their content is redacted by default (RAISE_DISTILL_DEV_TURNS=0).  Heuristic
    classification handles them instead (driven by structural markers only).
    """
    skip_indices: dict[int, tuple[TurnClass, int]] = {}
    classifiable: list[TurnRecord] = []
    for i, rec in enumerate(chunk):
        structural = classify_structural(rec)
        if structural is not None:
            skip_indices[i] = (structural, 5)
        elif rec.is_developer:
            # Privacy gate: classify heuristically to avoid sending redacted content to LLM
            skip_indices[i] = (classify_turn(rec), 5)
        else:
            classifiable.append(rec)

    if not classifiable:
        return [skip_indices.get(i, (TurnClass.NEUTRAL, 5)) for i in range(len(chunk))]

    llm_result = _classify_chunk_llm(classifiable, client, chunk_start, backend=backend)
    if llm_result is None:
        logger.info("Falling back to heuristic for chunk starting at %d", chunk_start)
        return [
            (classify_turn(rec), 3 if classify_turn(rec) is TurnClass.INSIGHT else 5)
            for rec in chunk
        ]

    llm_iter = iter(llm_result)
    return [
        skip_indices[i] if i in skip_indices else next(llm_iter, (TurnClass.NEUTRAL, 3))
        for i in range(len(chunk))
    ]


_COT_SYSTEM_PROMPT = """\
You are a verification agent for software engineering session transcripts.
Your task: decide whether a single assistant turn is a DURABLE INSIGHT worth persisting.

An insight MUST satisfy at least ONE of these positive criteria:
  • Identifies a recurring pattern or systemic behavior (not a one-time event)
  • Explains WHY something failed or worked (root cause, not just description)
  • Establishes a rule or principle applicable in future sessions or projects
  • Names a design risk, contract break, or silent assumption
  • Discovers dead code, orphaned artifacts, or a concrete gap/limitation

Classify as NOT an insight if ANY exclusion applies:
  • Progress narration: "I did X", "I finished Y", "Spawning agent", "Let me check"
  • Commit/MR/branch/Jira status: "MR !679 merged", "RAISE-X cerrado", "branch limpio"
  • Implementation description without a finding: just describing what was built
  • Operational instruction relevant only to this moment: "you need to run X now"
  • Confirmation that something works, without explaining why or what the principle is

DURABILITY TEST: Would this be valuable to a developer on a DIFFERENT project, 6 months later?
  If NO → not an insight. If YES and at least one positive criterion is met → insight.

Reason step by step, then give your verdict.

Output ONLY a JSON object:
{"reasoning": "<your step-by-step analysis>", "is_insight": true/false, "confidence": 1-5}
Confidence: 1=very uncertain, 5=very certain.
"""

_COT_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "is_insight": {"type": "boolean"},
        "confidence": {"type": "integer", "minimum": 1, "maximum": 5},
    },
    "required": ["reasoning", "is_insight", "confidence"],
}

# ── Episodic extraction models (S2) ──────────────────────────────────────────


class EpisodeInsight(BaseModel):
    """A single durable insight extracted from a session segment."""

    content: str
    durability: str  # "durable" | "ephemeral"
    confidence: float  # 0.0–1.0
    source_turns: list[int] = []


class EpisodeExtraction(BaseModel):
    """Result of running the episodic extractor on one Segment."""

    segment_id: str
    insights: list[EpisodeInsight]
    extraction_failed: bool
    backend_used: str


def _build_cot_prompt(record: TurnRecord) -> str:
    """Build the user-turn text for single-candidate CoT verification."""
    snippet = record.content_text[:2000].replace("\n", " ")
    return f"assistant: {snippet}"


def _cot_call_anthropic(record: TurnRecord, client: object) -> dict[str, object] | None:
    """Verify single INSIGHT candidate via Anthropic SDK with structured CoT output."""
    user_text = _build_cot_prompt(record)
    try:
        response = client.messages.create(  # type: ignore[attr-defined]
            model=_MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": _COT_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_text}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": _COT_OUTPUT_SCHEMA,
                    "name": "insight_verification",
                }
            },
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        return json.loads(text)  # type: ignore[return-value]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Anthropic CoT verify failed: %s", exc)
        return None


def _cot_call_openai_compat(
    record: TurnRecord, *, model: str, api_key: str
) -> dict[str, object] | None:
    """Verify single INSIGHT candidate via any OpenAI-compatible API."""
    import openai

    base_url = (
        "https://api.deepseek.com"
        if "deepseek" in model
        else "https://openrouter.ai/api/v1"
    )
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    user_text = _build_cot_prompt(record)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _COT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"{user_text}\n\n"
                        "Return ONLY a JSON object with keys: "
                        "reasoning (string), is_insight (boolean), confidence (1-5 integer). "
                        "No markdown fences, no explanation."
                    ),
                },
            ],
            max_tokens=512,
            response_format={"type": "json_object"},
        )
        text = response.choices[0].message.content or ""
        return json.loads(_extract_first_json_object(text))  # type: ignore[return-value]
    except Exception as exc:  # noqa: BLE001
        logger.warning("OpenAI-compat CoT verify failed (%s): %s", model, exc)
        return None


def _cot_call_subprocess(record: TurnRecord) -> dict[str, object] | None:
    """Verify single INSIGHT candidate via `claude -p` subprocess."""
    user_text = _build_cot_prompt(record)
    prompt = (
        f"{_COT_SYSTEM_PROMPT}\n\nTurn to verify:\n{user_text}\n\n"
        "Return ONLY the JSON object, no other text:\n"
        '{"reasoning": "...", "is_insight": true, "confidence": 4}'
    )
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", _MODEL],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode != 0:
            logger.warning("subprocess CoT verify failed: %s", proc.stderr[:200])
            return None
        return json.loads(  # type: ignore[return-value]
            _extract_first_json_object(proc.stdout.strip())
        )
    except (
        subprocess.TimeoutExpired,
        FileNotFoundError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        logger.warning("subprocess CoT verify error: %s", exc)
        return None


def _cot_single_call(
    record: TurnRecord, *, client: object, backend: str
) -> dict[str, object] | None:
    """Dispatch a single CoT verification call to the selected backend.

    AC7: Shared dispatch — no copy-pasted 4-branch logic; deepseek/openrouter share
    _cot_call_openai_compat, anthropic and subprocess each have their own thin wrapper.
    AC9: Reuses Stage-1 backend/model; no new routing introduced.
    """
    if backend == "anthropic":
        return _cot_call_anthropic(record, client)
    if backend == "deepseek":
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        if not deepseek_key:
            logger.warning("DEEPSEEK_API_KEY not set — deepseek CoT verify unavailable")
            return None
        return _cot_call_openai_compat(
            record, model=_DEEPSEEK_MODEL, api_key=deepseek_key
        )
    if backend == "openrouter":
        or_key = os.environ.get("OPENROUTER_API_KEY")
        or_model = os.environ.get("OPENROUTER_MODEL", "moonshotai/kimi-k2")
        if not or_key:
            logger.warning(
                "OPENROUTER_API_KEY not set — openrouter CoT verify unavailable"
            )
            return None
        return _cot_call_openai_compat(record, model=or_model, api_key=or_key)
    if backend == "subprocess":
        return _cot_call_subprocess(record)
    raise ValueError(f"Unknown backend {backend!r} for CoT verify. Choose: {BACKENDS}")


def verify_candidate(record: TurnRecord, *, client: object, backend: str) -> bool:
    """One CoT call: reason step-by-step, return True iff turn is a durable insight.

    AC1: Issues exactly ONE structured call per invocation.
    AC6: Fail-open on any error — returns True (retain candidate) to protect recall.
    """
    result = _cot_single_call(record, client=client, backend=backend)
    if result is None:
        logger.warning(
            "verify_candidate fail-open: retaining candidate at index %d", record.index
        )
        return True  # D3: fail-open
    try:
        return bool(result["is_insight"])
    except (KeyError, TypeError):
        logger.warning(
            "verify_candidate: malformed response at index %d — fail-open", record.index
        )
        return True  # D3: fail-open


def apply_two_stage(
    records: list[TurnRecord],
    classes: list[TurnClass],
    *,
    client: object | None = None,
    backend: str,
) -> list[TurnClass]:
    """Post-filter Stage 2: verify each INSIGHT candidate; demote rejects to NEUTRAL.

    AC2: Runs exactly K calls for K INSIGHT candidates; all other classes pass through.
    AC3: With verify=accept-all, output is byte-identical to Stage-1 (single-pass).
    AC8: Turns not marked INSIGHT by Stage 1 are never classified or mutated.
    """
    if client is None:
        import anthropic

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    out = list(classes)
    for i, (rec, cls) in enumerate(zip(records, classes, strict=False)):
        if cls is TurnClass.INSIGHT and not verify_candidate(
            rec, client=client, backend=backend
        ):
            out[i] = TurnClass.NEUTRAL
    return out


def classify_turns_llm_with_confidence(
    records: list[TurnRecord],
    *,
    client: object | None = None,
    backend: str | None = None,
) -> list[tuple[TurnClass, int]]:
    """Classify all records using LLM; return (TurnClass, confidence) pairs.

    No threshold is applied — returns raw classifier output including confidence
    scores 1-5. Use for eval / PR-curve computation.

    Args: same as classify_turns_llm.
    """
    resolved_backend = (
        backend
        or os.environ.get("RAISE_DISTILLATION_BACKEND")
        or ("anthropic" if client is not None else "deepseek")
    )
    if resolved_backend not in BACKENDS:
        raise ValueError(
            f"Unknown classifier backend {resolved_backend!r}. Choose: {BACKENDS}"
        )
    logger.info("LLM classifier backend (with_confidence): %s", resolved_backend)

    if client is None:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=api_key)

    effective_chunk_size = (
        _DEEPSEEK_CHUNK_SIZE if resolved_backend == "deepseek" else CHUNK_SIZE
    )
    pairs: list[tuple[TurnClass, int]] = []
    for chunk_start in range(0, len(records), effective_chunk_size):
        chunk = records[chunk_start : chunk_start + effective_chunk_size]
        pairs.extend(
            _classify_chunk(chunk, client, chunk_start, backend=resolved_backend)
        )
    return pairs


def classify_turns_llm(
    records: list[TurnRecord],
    *,
    client: object | None = None,
    backend: str | None = None,
) -> list[TurnClass]:
    """Classify all records using LLM (chunks of CHUNK_SIZE), with heuristic fallback.

    Applies RAISE_DISTILLATION_CONFIDENCE_MIN threshold: INSIGHT turns with
    confidence below the threshold are downgraded to NEUTRAL before returning.
    Default threshold=1 (no filtering). Use classify_turns_llm_with_confidence()
    to get raw confidence scores without threshold filtering.

    Args:
        records: Parsed turn records to classify.
        client: Anthropic client instance. Required only for the "anthropic" backend;
            ignored by deepseek/openrouter/subprocess. When provided and backend is
            unset, defaults to "anthropic" for backwards compatibility.
        backend: Which LLM backend to use. Choices: "anthropic", "deepseek",
            "openrouter", "subprocess". Defaults to RAISE_DISTILLATION_BACKEND env
            var, then "deepseek". No implicit fallback between backends — if the
            selected backend fails a chunk, that chunk falls back to heuristic only.

    TOOL_USE is handled structurally: turns with has_tools=True retain their
    text-based classification (decision/correction/etc) from the LLM.
    """
    min_confidence = int(os.environ.get("RAISE_DISTILLATION_CONFIDENCE_MIN", "1"))
    pairs = classify_turns_llm_with_confidence(records, client=client, backend=backend)
    if min_confidence <= 1:
        return [cls for cls, _ in pairs]
    return [
        cls
        if cls is not TurnClass.INSIGHT or conf >= min_confidence
        else TurnClass.NEUTRAL
        for cls, conf in pairs
    ]


# ── Episodic extraction (S2) ──────────────────────────────────────────────────

# Max chars per turn for episodic windows — longer than per-turn classifier
# (500 chars) because episodic context needs enough prose to surface arc meaning.
_EPISODE_TURN_CHARS = 2000

_EPISODE_SYSTEM_PROMPT = f"""\
You are an episodic insight extractor for software engineering session transcripts.

You receive a window of consecutive session turns forming a coherent conversational arc
(e.g. a debugging sequence, a blocker resolution, a decision and its confirmation).
Your task: extract DURABLE INSIGHTS that emerge from the arc as a whole — not from
individual turns in isolation.

An insight qualifies only if it meets ALL of:
{_DURABILITY_CRITERIA}

For each insight you find, identify:
- content: one concise sentence capturing the insight (≤ 120 chars)
- durability: "durable" (applicable in future contexts) or "ephemeral" (session-specific)
- confidence: 0.0–1.0
- source_turns: list of turn indices (from the [index] labels below) that together surface the insight

Return ONLY a JSON object (no markdown, no prose):
{{"insights": [
  {{"content": "...", "durability": "durable", "confidence": 0.9, "source_turns": [3, 4, 5]}}
]}}

If the window contains no qualifying insights, return {{"insights": []}}.
"""

_EPISODE_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "insights": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "durability": {"type": "string", "enum": ["durable", "ephemeral"]},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "source_turns": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["content", "durability", "confidence", "source_turns"],
            },
        }
    },
    "required": ["insights"],
}


def _build_episode_prompt(segment: Segment) -> str:
    """Build the user-turn text for an episodic extraction call.

    Each turn is prefixed with [index] role: to let the LLM reference
    specific turns in source_turns fields.
    """
    lines: list[str] = [
        f"Arc type: {segment.arc_type}",
        f"Turns {segment.start_turn}–{segment.end_turn} "
        f"(window group: {segment.window_group or 'none'})",
        "",
    ]
    for rec in segment.turns:
        snippet = rec.content_text[:_EPISODE_TURN_CHARS].replace("\n", " ")
        lines.append(f"[{rec.index}] {rec.turn_type.value}: {snippet}")
    return "\n".join(lines)


def _parse_episode_response(
    text: str, segment_id: str, backend: str
) -> EpisodeExtraction:
    """Parse JSON extraction response → EpisodeExtraction. Returns failed on parse error."""
    try:
        data = json.loads(_extract_first_json_object(text))
        insights = [
            EpisodeInsight(
                content=str(item["content"]),
                durability=str(item["durability"]),
                confidence=float(item["confidence"]),
                source_turns=[int(t) for t in item.get("source_turns", [])],
            )
            for item in data.get("insights", [])
        ]
        return EpisodeExtraction(
            segment_id=segment_id,
            insights=insights,
            extraction_failed=False,
            backend_used=backend,
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        logger.warning(
            "Episode extraction JSON parse failed: %s — raw: %.200s", exc, text
        )
        return EpisodeExtraction(
            segment_id=segment_id,
            insights=[],
            extraction_failed=True,
            backend_used=backend,
        )


def _extract_episode_anthropic(segment: Segment) -> EpisodeExtraction:
    """Extract insights from a segment via Anthropic SDK."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    user_text = _build_episode_prompt(segment)
    try:
        response = client.messages.create(  # type: ignore[attr-defined]
            model=_MODEL,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": _EPISODE_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_text}],
            output_config={  # pyright: ignore[reportArgumentType]
                "format": {
                    "type": "json_schema",
                    "schema": _EPISODE_OUTPUT_SCHEMA,
                    "name": "episode_extraction",
                }
            },
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        return _parse_episode_response(text, segment.session_id, "anthropic")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Anthropic episodic extractor failed: %s", exc)
        return EpisodeExtraction(
            segment_id=segment.session_id,
            insights=[],
            extraction_failed=True,
            backend_used="anthropic",
        )


def _extract_episode_openai_compat(
    segment: Segment, model: str, api_key: str
) -> EpisodeExtraction:
    """Extract via any OpenAI-compatible API (DeepSeek, OpenRouter, etc.).

    Uses text mode (not json_object) because episodic responses are longer than
    chunk responses — deepseek silently truncates json_object mode over ~600 chars.
    """
    import openai

    base_url = (
        "https://api.deepseek.com"
        if "deepseek" in model
        else "https://openrouter.ai/api/v1"
    )
    backend_name = "deepseek" if "deepseek" in model else "openrouter"
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    user_text = _build_episode_prompt(segment)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _EPISODE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"{user_text}\n\n"
                    "Return ONLY a JSON object with key 'insights' (array). "
                    "No markdown fences, no prose."
                ),
            },
        ],
        max_tokens=4096,
    )
    text = response.choices[0].message.content or ""
    return _parse_episode_response(
        _extract_first_json_object(text), segment.session_id, backend_name
    )


def _extract_episode_subprocess(segment: Segment) -> EpisodeExtraction:
    """Extract via `claude -p` subprocess — last resort, OAuth environments only."""
    user_text = _build_episode_prompt(segment)
    prompt = f"{_EPISODE_SYSTEM_PROMPT}\n\n{user_text}\n\nReturn ONLY valid JSON."
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if proc.returncode != 0:
            logger.warning(
                "subprocess episodic extractor failed: %s", proc.stderr[:200]
            )
            return EpisodeExtraction(
                segment_id=segment.session_id,
                insights=[],
                extraction_failed=True,
                backend_used="subprocess",
            )
        return _parse_episode_response(
            _extract_first_json_object(proc.stdout), segment.session_id, "subprocess"
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        logger.warning("subprocess episodic extractor error: %s", exc)
        return EpisodeExtraction(
            segment_id=segment.session_id,
            insights=[],
            extraction_failed=True,
            backend_used="subprocess",
        )


def _extract_episode_llm(segment: Segment, backend: str) -> EpisodeExtraction:
    """Dispatch to the selected backend for episodic extraction."""
    if backend == "anthropic":
        return _extract_episode_anthropic(segment)
    if backend == "deepseek":
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        if not deepseek_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY not set — deepseek backend unavailable"
            )
        return _extract_episode_openai_compat(segment, _DEEPSEEK_MODEL, deepseek_key)
    if backend == "openrouter":
        or_key = os.environ.get("OPENROUTER_API_KEY")
        if not or_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY not set — openrouter backend unavailable"
            )
        or_model = os.environ.get("OPENROUTER_MODEL", "moonshotai/kimi-k2")
        return _extract_episode_openai_compat(segment, or_model, or_key)
    if backend == "subprocess":
        return _extract_episode_subprocess(segment)
    raise ValueError(
        f"Unknown episodic extraction backend {backend!r}. Choose: {BACKENDS}"
    )


def extract_episode_insights(
    segment: Segment, backend: str | None = None
) -> EpisodeExtraction:
    """Extract durable insights from a session segment (window of turns).

    D4 (fail-loud): any runtime error from the backend returns extraction_failed=True.
    D5 (_DURABILITY_CRITERIA): shared durability criteria used in the extraction prompt.
    Empty segments (no turns) return immediately without a backend call.

    Args:
        segment: A Segment produced by detect_interesting_segments().
        backend: Backend to use. Choices: "anthropic", "deepseek", "openrouter",
                 "subprocess". Defaults to RAISE_DISTILLATION_BACKEND env var,
                 then "deepseek". Invalid backend name raises ValueError.
    """
    resolved_backend = (
        backend or os.environ.get("RAISE_DISTILLATION_BACKEND") or "deepseek"
    )
    if resolved_backend not in BACKENDS:
        raise ValueError(
            f"Unknown episodic extraction backend {resolved_backend!r}. Choose: {BACKENDS}"
        )
    if not segment.turns:
        return EpisodeExtraction(
            segment_id=segment.session_id,
            insights=[],
            extraction_failed=False,
            backend_used=resolved_backend,
        )
    try:
        return _extract_episode_llm(segment, resolved_backend)
    except Exception:  # noqa: BLE001
        logger.warning(
            "Episodic extraction failed for segment %s (backend=%s)",
            segment.session_id,
            resolved_backend,
        )
        return EpisodeExtraction(
            segment_id=segment.session_id,
            insights=[],
            extraction_failed=True,
            backend_used=resolved_backend,
        )
