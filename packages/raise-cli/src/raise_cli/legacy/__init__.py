"""Legacy install detection — single source of truth for residue scanning.

Doctor, ``rai clean``, and session advisory all consume ``scanner.scan_project()``
from this package.  No fingerprint is duplicated across surfaces.

Architecture: Epic RAISE-16227 design §Arquitectura.
"""
