"""Fitness-function false-positive calibration & promotion decision (RAISE-14679).

NOT to be confused with the top-level ``raise_cli.calibration`` package,
which is *velocity/estimation* calibration (``calibration.jsonl``,
``rai signal emit-work ... --event calibration``). This package answers a
different question: has a given CI fitness function (drift guard) earned
promotion from advisory (``allow_failure: true``) to hard-blocking, based on
its measured false-positive rate over recorded stories?
"""

from __future__ import annotations
