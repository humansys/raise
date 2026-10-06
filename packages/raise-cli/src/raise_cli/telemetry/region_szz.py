"""Carril B — atribución por región/add-only (S11899.2, E11899).

Implementa RegionAttributor que, dado un fix-commit add-only:
1. Detecta los hunks de adición pura (sin borrados).
2. Localiza el bloque encapsulante (AST → regex → ventana W=10).
3. Corre git blame sobre ese bloque en fix_commit^.
4. Determina la condición de autoría dominante por frecuencia.

Invariante honestidad: condition None ⇒ evidence["dominant_reason"] poblado.
Carril B nunca emite tier="high" — siempre "medium".
"""

from __future__ import annotations

import ast
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Literal, NamedTuple

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Tipos públicos
# ---------------------------------------------------------------------------

Condition = Literal["interactive", "batch_agent", "ai_unknown"]

# ---------------------------------------------------------------------------
# Mapas de condición (D3 — vive en region_szz, multitrack importa desde aquí)
# ---------------------------------------------------------------------------

_CONDITION_MAP: dict[str, Condition] = {
    "interactive": "interactive",
    "batch_agent": "batch_agent",
    "ai_unknown": "ai_unknown",
    "ai_session_unresolved": "ai_unknown",
}

# ---------------------------------------------------------------------------
# Constantes internas
# ---------------------------------------------------------------------------

_WINDOW_W: int = 10

_HUNK_RE = re.compile(r"^@@ -\d+(?:,(\d+))? \+(\d+)(?:,\d+)? @@")
_FILE_RE = re.compile(r"^--- a/(.+)$")
_DEF_CLASS_RE = re.compile(r"^(\s*)((?:async\s+)?def |class )(\w+)")


# ---------------------------------------------------------------------------
# Modelo de resultado
# ---------------------------------------------------------------------------


class RegionResult(BaseModel):
    """Resultado de atribución de una región add-only.

    Un resultado por hunk add-only procesado satisfactoriamente.
    Invariante: dominant_condition is None ⇒ evidence["dominant_reason"] poblado.
    """

    fix_commit: str
    """SHA del commit add-only analizado."""

    enclosing_block: str | None
    """Nombre del bloque encapsulante (función/clase), o None si es top-level."""

    introducer_commit: str | None
    """SHA del commit introductor: PRIMER commit único en orden de blame del bloque.
    (blame_shas se deduplica → no es 'el más frecuente'; el ranking line-weighted
    es refinamiento de precisión diferido a S4/RAISE-11962.)"""

    dominant_condition: Condition | None
    """Condición de autoría dominante. None si no hay blamed commits blameable."""

    evidence: dict[str, object]
    """Evidencia del análisis. Campos: hunk_range, blamed_commits,
    condition_frequencies, dominant_reason, block_strategy."""


# ---------------------------------------------------------------------------
# Tipo interno para bloques encapsulantes
# ---------------------------------------------------------------------------


class _Block(NamedTuple):
    name: str | None
    start: int
    end: int
    strategy: str


# ---------------------------------------------------------------------------
# Funciones helper de diff / git
# ---------------------------------------------------------------------------


def _run_git(args: list[str], repo_path: Path) -> str:
    """Ejecuta git y retorna stdout. Levanta CalledProcessError en fallo."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=str(repo_path),
        timeout=30,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, ["git", *args], result.stdout, result.stderr
        )
    return result.stdout.strip()


def _parse_addonly_hunks(diff: str) -> list[tuple[str, int]]:
    """Parse diff --unified=0 y extrae hunks add-only.

    Retorna [] si ALGÚN hunk tiene borrados (minus count > 0).
    Retorna list[(file_path, new_start_line)] para hunks add-only.

    Reglas:
    - `@@ -start,count +new_start,... @@`: count > 0 → borrado → return []
    - count ausente en `@@ -start +... @@` equivale a count=1 → borrado
    - count=0 → hunk add-only ✓
    """
    current_file: str | None = None
    hunks: list[tuple[str, int]] = []

    for line in diff.splitlines():
        fm = _FILE_RE.match(line)
        if fm:
            current_file = fm.group(1)
            continue

        hm = _HUNK_RE.match(line)
        if hm and current_file:
            minus_count_str = hm.group(1)  # None si se omitió la coma
            minus_count = int(minus_count_str) if minus_count_str is not None else 1
            new_start = int(hm.group(2))

            if minus_count > 0:
                # Tiene borrados → no es add-only
                return []

            hunks.append((current_file, new_start))

    return hunks


def _ast_enclosing_block(
    tree: ast.AST, insert_line: int, total_lines: int
) -> _Block | None:
    """Encuentra el bloque (función/clase) más interno que contiene insert_line.

    Recorre todos los nodos del AST y devuelve el de menor rango que contenga
    la línea de inserción. 'Menor rango' = innermost (más específico).
    """
    best: _Block | None = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        start = node.lineno
        end = getattr(node, "end_lineno", None) or total_lines
        if start <= insert_line <= end and (
            best is None or (end - start) < (best.end - best.start)
        ):
            best = _Block(name=node.name, start=start, end=end, strategy="ast")
    return best


def _regex_enclosing_block(lines: list[str], insert_line: int) -> _Block | None:
    """Fallback regex cuando AST falla (SyntaxError en el archivo).

    Escanea hacia atrás desde insert_line buscando `def` / `class`.
    Calcula end como la siguiente definición al mismo nivel de indentación.
    """
    # Convertimos insert_line (1-indexed) a 0-indexed
    search_to = min(insert_line - 1, len(lines))
    for i in range(search_to - 1, -1, -1):
        m = _DEF_CLASS_RE.match(lines[i])
        if m:
            name = m.group(3)
            indent = len(m.group(1))
            start = i + 1  # 1-indexed
            # Busca la siguiente definición al mismo o menor nivel de indentación
            end = len(lines)
            for j in range(i + 1, len(lines)):
                jline = lines[j]
                if not jline.strip():
                    continue
                jind = len(jline) - len(jline.lstrip())
                if jind <= indent and _DEF_CLASS_RE.match(jline):
                    end = j  # línea j+1 (1-indexed) comienza la siguiente def
                    break
            return _Block(name=name, start=start, end=end, strategy="regex")
    return None


def _resolve_enclosing_block(
    fix_commit: str,
    file_path: str,
    insert_line: int,
    repo_path: Path,
) -> _Block:
    """Determina el bloque encapsulante de una inserción add-only.

    Estrategias (en orden):
    1. AST: analiza el árbol Python y localiza función/clase más interna.
       Si no hay función encapsulante (código top-level) → window.
    2. Regex: fallback cuando el archivo tiene SyntaxError.
    3. Window: W=10 líneas alrededor de insert_line.

    Returns:
        _Block(name, start, end, strategy) — name=None para código top-level.
    """
    try:
        content = _run_git(["show", f"{fix_commit}:{file_path}"], repo_path)
    except subprocess.CalledProcessError:
        start = max(1, insert_line - _WINDOW_W)
        end = insert_line + _WINDOW_W
        return _Block(name=None, start=start, end=end, strategy="window")

    lines = content.splitlines()
    n_lines = len(lines)

    # Estrategia 1: AST
    try:
        tree = ast.parse(content)
        block = _ast_enclosing_block(tree, insert_line, n_lines)
        if block:
            return block
        # AST parseó OK pero no hay función encapsulante → código top-level → window
        start = max(1, insert_line - _WINDOW_W)
        end = min(n_lines, insert_line + _WINDOW_W)
        return _Block(name=None, start=start, end=end, strategy="window")
    except SyntaxError:
        pass

    # Estrategia 2: Regex
    block = _regex_enclosing_block(lines, insert_line)
    if block:
        return block

    # Estrategia 3: Window (último recurso)
    start = max(1, insert_line - _WINDOW_W)
    end = min(n_lines, insert_line + _WINDOW_W)
    return _Block(name=None, start=start, end=end, strategy="window")


def _git_blame_lines(
    file_path: str,
    start: int,
    end: int,
    ref: str,
    repo_path: Path,
) -> list[str]:
    """Ejecuta git blame --porcelain en [start, end] en ref.

    Retorna lista de SHAs únicos en orden de primera aparición.
    Retorna [] si el rango es inválido o el archivo no existe en ref.
    """
    if start > end:
        return []

    try:
        output = _run_git(
            [
                "blame",
                "--porcelain",
                f"-L{start},{end}",
                ref,
                "--",
                file_path,
            ],
            repo_path,
        )
    except subprocess.CalledProcessError:
        return []

    hashes: list[str] = []
    seen: set[str] = set()
    sha_re = re.compile(r"^[0-9a-f]{40}")
    for line in output.splitlines():
        if len(line) >= 40 and sha_re.match(line):
            h = line[:40]
            if h not in seen:
                seen.add(h)
                hashes.append(h)
    return hashes


def _compute_dominant_condition(
    blame_shas: list[str],
    repo_path: Path,
    claude_projects_dir: Path | None,
) -> tuple[Condition | None, dict[str, int], str | None]:
    """Calcula la condición de autoría dominante a partir de blame SHAs.

    Para cada SHA:
    1. Extrae el trailer Claude-Session via SzzAttributor.resolve_trailer.
    2. Crea un IntroducerResult mínimo.
    3. Llama a resolve_authoring_condition para obtener la condición final.
    4. Mapea al Condition de 3 valores vía _CONDITION_MAP.

    Retorna (dominant_condition, raw_freq_dict, reason).
    dominant_condition=None si no hay blamed SHAs o todas son "unmapped".
    """
    # Importaciones locales para evitar ciclos y acelerar import del módulo
    from raise_cli.telemetry.defect_attribution import resolve_authoring_condition
    from raise_cli.telemetry.szz import IntroducerResult, SzzAttributor

    if not blame_shas:
        return None, {}, "no blameable lines in enclosing block"

    attributor = SzzAttributor()
    raw_conditions: list[str] = []

    for sha in blame_shas:
        session_id, raw = attributor.resolve_trailer(sha, repo_path)
        intro = IntroducerResult(
            bug_key="",
            fix_commit="",
            introducer_commit=sha,
            introducer_author="",
            introducer_session_id=session_id,
            authoring_condition=raw,
            confidence=0.5,
            evidence=[],
        )
        record = resolve_authoring_condition(
            intro,
            repo_path=repo_path,
            claude_projects_dir=claude_projects_dir,
        )
        raw_conditions.append(record.authoring_condition)

    # Frecuencia de condiciones raw
    freq = Counter(raw_conditions)

    # Mapear a Condition (3-valor)
    mapped_freq: Counter[str] = Counter()
    for cond, count in freq.items():
        mapped = _CONDITION_MAP.get(cond)
        if mapped is not None:
            mapped_freq[mapped] += count
        else:
            mapped_freq[f"unmapped:{cond}"] += count

    # Condición dominante = la más frecuente que sea Condition válida
    dominant_entries = [
        (k, v) for k, v in mapped_freq.items() if not k.startswith("unmapped:")
    ]

    if not dominant_entries:
        unmapped_conds = [c for c in freq if _CONDITION_MAP.get(c) is None]
        return None, dict(freq), f"condición no reconocida: {unmapped_conds!r}"

    dominant_key = max(dominant_entries, key=lambda x: x[1])[0]
    dominant: Condition = dominant_key  # type: ignore[assignment]
    return dominant, dict(freq), None


# ---------------------------------------------------------------------------
# RegionAttributor — implementación completa (T3)
# ---------------------------------------------------------------------------


class RegionAttributor:
    """Atribuye un fix-commit add-only por análisis de región encapsulante.

    Carril B del pipeline multi-carril (E11899).
    tier="medium" fijo — nunca "high".
    """

    def __init__(self, claude_projects_dir: Path | None = None) -> None:
        """Inicializa el atribuidor.

        Args:
            claude_projects_dir: Directorio de sesiones CC (para tests).
                None → usa ~/.claude/projects (producción).
        """
        self._claude_projects_dir = claude_projects_dir

    def attribute_region(
        self,
        fix_commit: str,
        repo_path: Path,
    ) -> list[RegionResult]:
        """Atribuye un fix-commit add-only por región encapsulante.

        Pipeline:
        1. Obtiene el diff --unified=0 del commit.
        2. _parse_addonly_hunks: retorna [] si el commit tiene borrados.
        3. Para cada hunk add-only:
            a. _resolve_enclosing_block: AST → regex → window.
            b. _git_blame_lines: blame del bloque en fix_commit^.
            c. _compute_dominant_condition: condición dominante por frecuencia.
        4. Construye un RegionResult por hunk.

        Returns:
            Lista de RegionResult. Vacía si el commit no es add-only.
        """
        # 1. Diff
        try:
            diff = _run_git(
                ["diff", f"{fix_commit}^..{fix_commit}", "--unified=0"],
                repo_path,
            )
        except subprocess.CalledProcessError:
            return []

        # 2. Detectar hunks add-only
        hunks = _parse_addonly_hunks(diff)
        if not hunks:
            return []

        results: list[RegionResult] = []

        for file_path, insert_line in hunks:
            # 3a. Bloque encapsulante
            block = _resolve_enclosing_block(
                fix_commit, file_path, insert_line, repo_path
            )

            # 3b. Rango para blame: líneas que EXISTÍAN antes de la inserción
            #     blame_end = insert_line - 1 (las líneas nuevas no existen en el padre)
            blame_start = block.start
            blame_end = max(block.start, insert_line - 1)

            # 3c. Blame al padre
            blame_shas = _git_blame_lines(
                file_path,
                blame_start,
                blame_end,
                f"{fix_commit}^",
                repo_path,
            )

            # 3d. Condición dominante
            dominant, freq_dict, reason = _compute_dominant_condition(
                blame_shas, repo_path, self._claude_projects_dir
            )

            # Introductor = PRIMER commit único en orden de blame.
            # blame_shas ya viene deduplicado (SHAs únicos en orden de aparición),
            # así que most_common(1) siempre devuelve el primero — NO es por
            # frecuencia. El ranking line-weighted es refinamiento de S4 (RAISE-11962).
            introducer: str | None = blame_shas[0] if blame_shas else None

            results.append(
                RegionResult(
                    fix_commit=fix_commit,
                    enclosing_block=block.name,
                    introducer_commit=introducer,
                    dominant_condition=dominant,
                    evidence={
                        "block_strategy": block.strategy,
                        "blamed_commits": blame_shas,
                        "condition_frequencies": freq_dict,
                        "dominant_reason": reason or "",
                        "hunk_range": [blame_start, blame_end],
                    },
                )
            )

        return results
