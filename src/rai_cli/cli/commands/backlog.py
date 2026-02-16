"""CLI commands for backlog management and external provider integration.

This module provides the `rai backlog` command group for managing project backlogs
and integrating with external providers (JIRA, GitLab, etc.).

Example:
    $ rai backlog auth --provider jira    # Authenticate with JIRA
    $ rai backlog pull --source jira --epic DEMO-1  # Pull epic from JIRA
    $ rai backlog push --source jira --epic E-DEMO  # Push stories to JIRA
    $ rai backlog status --epic E-DEMO    # Check authorization status
"""

from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console

backlog_app = typer.Typer(
    name="backlog",
    help="Manage backlog and external provider integrations",
    no_args_is_help=True,
)

console = Console()


def _get_sync_dir(project: str) -> Path:
    """Get sync directory path for project."""
    return Path(project).resolve() / ".raise" / "rai" / "sync"


def _init_jira_client() -> tuple[object, str]:
    """Initialize JIRA client from stored credentials with auto-refresh.

    Checks token expiry and refreshes automatically if needed.
    Stores refreshed token back to credentials file.

    Returns:
        Tuple of (JiraClient, cloud_id)

    Raises:
        typer.Exit: If credentials not found or refresh fails
    """
    try:
        from rai_cli.config.paths import get_credentials_path
        from rai_pro.providers.auth.credentials import load_token, store_token
        from rai_pro.providers.jira.client import JiraClient
        from rai_pro.providers.jira.oauth import (
            OAuthError,
            is_token_expired,
            refresh_access_token,
        )
    except ImportError:
        console.print(
            "[red]Error:[/red] rai-pro is required for JIRA integration.\n"
            "Install with: pip install rai-cli[pro]"
        )
        raise typer.Exit(code=1) from None

    credentials_path = get_credentials_path()
    token = load_token("jira", credentials_path)

    if not token:
        console.print(
            "[red]Error:[/red] No JIRA credentials found.\n"
            "Run: rai backlog auth --provider jira"
        )
        raise typer.Exit(code=1)

    # Auto-refresh expired tokens
    if is_token_expired(token):
        client_id = os.getenv("JIRA_CLIENT_ID", "")
        client_secret = os.getenv("JIRA_CLIENT_SECRET", "")

        if not client_id or not client_secret:
            console.print(
                "[red]Error:[/red] Token expired and JIRA_CLIENT_ID/JIRA_CLIENT_SECRET "
                "not set for refresh.\nRun: rai backlog auth --provider jira"
            )
            raise typer.Exit(code=1)

        try:
            token = refresh_access_token(token, client_id, client_secret)
            store_token("jira", token, credentials_path)
            console.print("[dim]Token refreshed automatically.[/dim]")
        except OAuthError as e:
            console.print(
                f"[red]Error:[/red] Token refresh failed: {e}\n"
                "Run: rai backlog auth --provider jira"
            )
            raise typer.Exit(code=1) from e

    cloud_id = os.getenv("JIRA_CLOUD_ID", "")
    if not cloud_id:
        console.print(
            "[red]Error:[/red] JIRA_CLOUD_ID environment variable not set.\n"
            "Get it from: https://api.atlassian.com/oauth/token/accessible-resources"
        )
        raise typer.Exit(code=1)

    client = JiraClient(
        cloud_id=cloud_id,
        access_token=token["access_token"],
    )
    return client, cloud_id


@backlog_app.command()
def auth(
    provider: str = typer.Option(
        ...,
        "--provider",
        "-p",
        help="External provider to authenticate with (e.g., 'jira')",
    ),
) -> None:
    """Authenticate with an external backlog provider.

    Initiates OAuth 2.0 flow to authenticate with the specified provider.
    Credentials are stored securely in ~/.rai/credentials.json with encryption.

    Supported providers:
        - jira: Atlassian JIRA Cloud

    Environment variables (optional):
        - JIRA_CLIENT_ID: Custom OAuth client ID
        - JIRA_CLIENT_SECRET: Custom OAuth client secret

    Examples:
        $ rai backlog auth --provider jira
        $ JIRA_CLIENT_ID=xxx JIRA_CLIENT_SECRET=yyy rai backlog auth --provider jira
    """
    # Validate provider
    if provider.lower() not in ["jira"]:
        console.print(
            f"[red]Error:[/red] Provider '{provider}' is not supported.\n"
            f"Supported providers: jira",
            style="red",
        )
        raise typer.Exit(code=1)

    # Import provider modules
    try:
        from rai_cli.config.paths import get_credentials_path
        from rai_pro.providers.jira.oauth import (
            OAuthError,
            authenticate,
            get_current_user,
        )
    except ImportError:
        console.print(
            "[red]Error:[/red] rai-pro is required for JIRA integration.\n"
            "Install with: pip install rai-cli[pro]"
        )
        raise typer.Exit(code=1) from None

    # Get credentials path
    credentials_path = get_credentials_path()

    # Get OAuth credentials from environment or use defaults
    if provider.lower() == "jira":
        client_id = os.getenv("JIRA_CLIENT_ID", "")
        client_secret = os.getenv("JIRA_CLIENT_SECRET", "")

        if not client_id or not client_secret:
            console.print(
                "[yellow]Warning:[/yellow] Using demo OAuth credentials.\n"
                "For production use, set JIRA_CLIENT_ID and JIRA_CLIENT_SECRET environment variables.",
                style="yellow",
            )
            # Demo credentials (replace with actual demo app credentials)
            client_id = os.getenv("JIRA_CLIENT_ID", "demo-client-id")
            client_secret = os.getenv("JIRA_CLIENT_SECRET", "demo-client-secret")

        # Run OAuth flow
        try:
            console.print(
                f"[bold]Authenticating with {provider.upper()}...[/bold]"
            )

            token = authenticate(
                client_id=client_id,
                client_secret=client_secret,
                credentials_path=credentials_path,
            )

            # Get user info to display confirmation
            user_info = get_current_user(token["access_token"])
            email = user_info.get("email", "Unknown")

            console.print(
                f"\n[green]✓ Authenticated as {email}[/green]",
                style="bold green",
            )
            console.print(
                f"Credentials stored securely in: {credentials_path}",
                style="dim",
            )

        except OAuthError as e:
            console.print(
                f"\n[red]OAuth Error:[/red] {e}",
                style="red",
            )
            raise typer.Exit(code=1) from e

        except Exception as e:
            # Handle network errors and other unexpected errors
            console.print(
                f"\n[red]Error:[/red] {e}",
                style="red",
            )
            raise typer.Exit(code=1) from e


@backlog_app.command()
def pull(
    source: str = typer.Option(
        ..., "--source", "-s", help="Provider to pull from (jira)"
    ),
    epic: str = typer.Option(
        ..., "--epic", "-e", help="JIRA epic key (e.g., DEMO-1)"
    ),
    epic_id: str = typer.Option(
        "", "--epic-id", help="Local epic ID to assign (default: auto-generate)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview without executing"
    ),
    project: str = typer.Option(
        ".", "--project", "-p", help="Project root path"
    ),
) -> None:
    """Pull epic and stories from JIRA to local sync state.

    Reads epic and its stories from JIRA, maps them to local IDs,
    and stores sync state in .raise/rai/sync/state.json.

    Examples:
        $ rai backlog pull --source jira --epic DEMO-1
        $ rai backlog pull --source jira --epic DEMO-1 --epic-id E-DEMO --dry-run
    """
    if source.lower() != "jira":
        console.print(f"[red]Error:[/red] Source '{source}' not supported. Use 'jira'.")
        raise typer.Exit(code=1)

    try:
        from rai_pro.providers.jira.sync import pull_epic as _pull_epic
        from rai_pro.providers.jira.sync_state import SyncState, load_state, save_state
    except ImportError:
        console.print(
            "[red]Error:[/red] rai-pro is required for JIRA integration.\n"
            "Install with: pip install rai-cli[pro]"
        )
        raise typer.Exit(code=1) from None

    client, cloud_id = _init_jira_client()
    sync_dir = _get_sync_dir(project)

    # Load or create state
    state = load_state(sync_dir)
    project_key = epic.split("-")[0]
    if state is None:
        state = SyncState(cloud_id=cloud_id, project_key=project_key)

    # Auto-generate epic_id if not provided
    local_epic_id = epic_id or f"E-{project_key}"

    try:
        result = _pull_epic(
            client=client,  # type: ignore[arg-type]
            epic_key=epic,
            epic_id=local_epic_id,
            state=state,
            dry_run=dry_run,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e

    # Display results
    prefix = "[yellow][DRY RUN][/yellow] " if dry_run else ""

    console.print(f"\n{prefix}[bold]Pulling from JIRA...[/bold]\n")
    status_label = "new" if result.epic_imported else "updated"
    console.print(
        f"Epic: {result.epic_key} \"{result.epic_summary}\" "
        f"[{result.epic_status}] → {local_epic_id} ({status_label})"
    )

    if result.story_details:
        console.print("\nStories:")
        for detail in result.story_details:
            s_action = detail.get("action", "imported")
            s_icon = "✓" if s_action == "imported" else "↻"
            console.print(
                f"  {s_icon} {detail.get('jira_key', '?')}: "
                f"\"{detail.get('summary', '')}\" "
                f"[{detail.get('status', '?')}] → {detail.get('local_id', '?')}"
            )

    console.print(
        f"\nSummary: {result.stories_imported} imported, "
        f"{result.stories_updated} updated."
    )

    if not dry_run:
        save_state(state, sync_dir)
        console.print(f"State saved to {sync_dir / 'state.json'}", style="dim")


@backlog_app.command()
def push(
    source: str = typer.Option(
        ..., "--source", "-s", help="Provider to push to (jira)"
    ),
    epic: str = typer.Option(
        ..., "--epic", "-e", help="Local epic ID (e.g., E-DEMO)"
    ),
    stories_input: str = typer.Option(
        "", "--stories", help="Comma-separated story definitions: id:title,id:title"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview without executing"
    ),
    project: str = typer.Option(
        ".", "--project", "-p", help="Project root path"
    ),
) -> None:
    """Push local stories to JIRA under mapped epic.

    Creates JIRA stories linked to the parent epic. Idempotent — re-running
    won't create duplicates. Requires prior pull to map the epic.

    Examples:
        $ rai backlog push --source jira --epic E-DEMO \\
            --stories "S-DEMO.1:Define governance,S-DEMO.2:Create checklist"
        $ rai backlog push --source jira --epic E-DEMO --dry-run
    """
    if source.lower() != "jira":
        console.print(f"[red]Error:[/red] Source '{source}' not supported. Use 'jira'.")
        raise typer.Exit(code=1)

    try:
        from rai_pro.providers.jira.sync import LocalStory  # noqa: I001
        from rai_pro.providers.jira.sync import push_stories as _push_stories
        from rai_pro.providers.jira.sync_state import load_state, save_state
    except ImportError:
        console.print(
            "[red]Error:[/red] rai-pro is required for JIRA integration.\n"
            "Install with: pip install rai-cli[pro]"
        )
        raise typer.Exit(code=1) from None

    client, _cloud_id = _init_jira_client()
    sync_dir = _get_sync_dir(project)

    state = load_state(sync_dir)
    if state is None:
        console.print(
            "[red]Error:[/red] No sync state found. Run pull first:\n"
            "  rai backlog pull --source jira --epic <JIRA_KEY>"
        )
        raise typer.Exit(code=1)

    # Parse stories from input
    local_stories: list[LocalStory] = []
    if stories_input:
        for part in stories_input.split(","):
            parts = part.strip().split(":", 1)
            if len(parts) == 2:
                local_stories.append(
                    LocalStory(story_id=parts[0].strip(), title=parts[1].strip())
                )

    if not local_stories:
        console.print(
            "[red]Error:[/red] No stories provided.\n"
            "Use --stories 'S-DEMO.1:Title One,S-DEMO.2:Title Two'"
        )
        raise typer.Exit(code=1)

    try:
        result = _push_stories(
            client=client,  # type: ignore[arg-type]
            epic_id=epic,
            stories=local_stories,
            state=state,
            dry_run=dry_run,
        )
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e

    # Display results
    prefix = "[yellow][DRY RUN][/yellow] " if dry_run else ""
    console.print(f"\n{prefix}[bold]Pushing stories to JIRA...[/bold]\n")
    console.print(f"Epic: {epic} → {result.jira_epic_key}\n")

    if result.created_details:
        label = "Would create" if dry_run else "Created"
        console.print(f"{label}:")
        for detail in result.created_details:
            jira_key = detail.get("jira_key", "pending")
            console.print(
                f"  ✓ {detail['story_id']}: \"{detail['title']}\" → {jira_key}"
            )

    if result.skipped_details:
        console.print("\nSkipped (already synced):")
        for sid in result.skipped_details:
            jira_key = state.stories.get(sid, None)
            key_str = jira_key.jira_key if jira_key else "?"
            console.print(f"  - {sid} ({key_str})")

    console.print(
        f"\nSummary: {result.created} created, {result.skipped} skipped."
    )

    if not dry_run:
        save_state(state, sync_dir)
        console.print(f"State saved to {sync_dir / 'state.json'}", style="dim")


@backlog_app.command()
def status(
    epic: str = typer.Option(
        ..., "--epic", "-e", help="Local epic ID (e.g., E-DEMO)"
    ),
    project: str = typer.Option(
        ".", "--project", "-p", help="Project root path"
    ),
) -> None:
    """Show sync and authorization status for epic stories.

    Reads local sync state (no JIRA API calls). Shows which stories
    are authorized to work on based on their JIRA status.

    Examples:
        $ rai backlog status --epic E-DEMO
    """
    try:
        from rai_pro.providers.jira.sync import check_authorization
        from rai_pro.providers.jira.sync_state import load_state
    except ImportError:
        console.print(
            "[red]Error:[/red] rai-pro is required for JIRA integration.\n"
            "Install with: pip install rai-cli[pro]"
        )
        raise typer.Exit(code=1) from None

    sync_dir = _get_sync_dir(project)
    state = load_state(sync_dir)

    if state is None:
        console.print(
            "[red]Error:[/red] No sync state found. Run pull first:\n"
            "  rai backlog pull --source jira --epic <JIRA_KEY>"
        )
        raise typer.Exit(code=1)

    # Check epic exists
    if epic not in state.epics:
        console.print(f"[red]Error:[/red] Epic {epic} not found in sync state.")
        raise typer.Exit(code=1)

    epic_mapping = state.epics[epic]
    console.print(
        f"\n[bold]Authorization status for {epic}[/bold] "
        f"(JIRA: {epic_mapping.jira_key})\n"
    )

    # Check each story
    epic_prefix = epic.removeprefix("E-")
    story_ids = sorted(
        [sid for sid in state.stories if sid.startswith(f"S-{epic_prefix}.")]
    )

    if not story_ids:
        console.print("  No stories synced for this epic.")
        return

    for story_id in story_ids:
        result = check_authorization(state, story_id)
        if result.authorized:
            console.print(
                f"  [green]✓[/green] {story_id}: {result.jira_status} "
                f"({result.jira_key}) — Ready to work"
            )
        else:
            console.print(
                f"  [red]✗[/red] {story_id}: {result.jira_status} "
                f"({result.jira_key}) — Awaiting authorization"
            )

    if state.last_sync_at:
        console.print(
            f"\nLast sync: {state.last_sync_at.strftime('%Y-%m-%d %H:%M UTC')}",
            style="dim",
        )
    console.print(
        "Run 'rai backlog pull --source jira --epic <KEY>' to refresh.",
        style="dim",
    )
