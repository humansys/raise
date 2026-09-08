"""QR code rendering adapter for rai session qr.

Wraps qrcode.QRCode.print_ascii() to render a scannable QR in the terminal.
No PIL required — ASCII output works in any terminal.

Architecture: E15815 Session Control Plane, S15815.4
"""

from __future__ import annotations

import getpass

import qrcode


def build_ssh_command(
    *,
    host: str,
    session_id: str,
    username: str | None = None,
    control: bool = False,
) -> str:
    """Build the SSH command encoded in the QR code.

    Args:
        host: IP address of the remote host.
        session_id: Runtime session identifier (used as tmux session name).
        username: SSH username. Defaults to current user.
        control: If True, attach in writable mode; if False, read-only (-r).

    Returns:
        A ready-to-run SSH command string.
    """
    user = username or getpass.getuser()
    tmux_name = f"rai-{session_id}"
    attach_flags = "attach" if control else "attach -r"
    return f"ssh -t {user}@{host} 'tmux {attach_flags} -t {tmux_name}'"


def build_mosh_command(
    *,
    host: str,
    session_id: str,
    username: str | None = None,
    control: bool = False,
) -> str:
    """Build the mosh command encoded in the QR code.

    Args:
        host: IP address of the remote host.
        session_id: Runtime session identifier (used as tmux session name).
        username: SSH username. Defaults to current user.
        control: If True, attach in writable mode; if False, read-only (-r).

    Returns:
        A ready-to-run mosh command string.
    """
    user = username or getpass.getuser()
    tmux_name = f"rai-{session_id}"
    attach_flags = "attach" if control else "attach -r"
    return f"mosh {user}@{host} -- tmux {attach_flags} -t {tmux_name}"


def render_qr(data: str) -> None:
    """Render a QR code to stdout as ASCII art.

    Args:
        data: The string to encode in the QR code.
    """
    qr = qrcode.QRCode(
        error_correction=1,  # ERROR_CORRECT_L (L=1, M=0, Q=3, H=2)
        box_size=1,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
