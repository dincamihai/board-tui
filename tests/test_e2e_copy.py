"""E2E tests for copy actions in BoardApp.

Tests 'c' copies slug to clipboard and 'C' copies title to clipboard.
Mocks subprocess.run for clipboard commands (xclip/pbcopy).
Uses Textual's App.run_test() with async pilot.
"""

import subprocess
from pathlib import Path
from unittest import mock

import pytest

from board_tui.app import BoardApp

# ------ -------------------------- ------ ------------ ------ ----------- ----
# Fixtures: task markdown content
# ------ ---------------------------------- ---- ---------- ------ ----------- ----

_TASK_SLUG_FIX_LOGIN = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Fix login bug

The user reports that login fails with stale sessions.
"""

_TASK_TITLE_OAUTH2 = """---
column: Backlog
order: 20
created: 2026-04-21
---

# Implement OAuth2 flow

Add OAuth2 authentication support for third-party providers.
"""

_TASK_TITLE_STANDALONE = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Standalone summary task

A simple task with a short title for copy testing.
"""


def _write_tasks(tasks_dir: Path, entries: list[tuple[str, str]]) -> None:
    """Write task markdown files into the given directory."""
    for slug, content in entries:
        tasks_dir.joinpath(f"{slug}.md").write_text(content)


def _make_app(tasks_dir: Path, user: str = "alice") -> BoardApp:
    """Create a BoardApp bound to the given tasks directory."""
    return BoardApp(
        tasks_dir=str(tasks_dir),
        columns=["Backlog", "In Progress", "Done"],
        user=user,
    )


# ------ -------------------------- ------ ------------ ------ ----------- ----
# Mock helpers
# ------ -------------------- ------ -------- ---- ---------- ------ ----------- ----


def _mock_subprocess_run(*args, **kwargs):
    """Side-effect for subprocess.run — stores the last call for inspection."""
    _mock_subprocess_run.last_call = (args, kwargs)
    return mock.MagicMock(returncode=0)


_mock_subprocess_run.last_call = None


def _reset_mock() -> None:
    """Reset the module-level mock state (needed for test isolation)."""
    _mock_subprocess_run.last_call = None


# ------ -------------------------- ------ ------------ ------ ----------- ----
# Test: 'c' copies slug to clipboard
# ------ -------------------- ------ -------- ---- ---------- ------ ----------- ----


@pytest.mark.asyncio
async def test_c_copies_slug_to_clipboard(tmp_path: Path):
    """Pressing 'c' copies the selected task's slug to the clipboard."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("fix-login-bug", _TASK_SLUG_FIX_LOGIN)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            # Press 'c' to copy slug
            await pilot.press("c")
            await pilot.pause()

            # Verify subprocess.run was invoked
            assert _mock_subprocess_run.last_call is not None
            _, kwargs = _mock_subprocess_run.last_call
            assert kwargs["input"] == "fix-login-bug"


@pytest.mark.asyncio
async def test_c_copies_correct_slug_with_dash(tmp_path: Path):
    """'c' correctly copies slugs containing hyphens."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("implement-oauth2-flow", _TASK_TITLE_OAUTH2)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("c")
            await pilot.pause()

            _, kwargs = _mock_subprocess_run.last_call
            assert kwargs["input"] == "implement-oauth2-flow"


# ------ -------------------------- ------ ------------ ------ ----------- ----
# Test: 'C' copies title to clipboard
# ------ -------------------- ------ -------- ---- ---------- ------ ----------- ----


@pytest.mark.asyncio
async def test_c_upper_copies_title_to_clipboard(tmp_path: Path):
    """Pressing 'C' copies the selected task's title to the clipboard."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("fix-login-bug", _TASK_SLUG_FIX_LOGIN)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("C")
            await pilot.pause()

            _, kwargs = _mock_subprocess_run.last_call
            assert kwargs["input"] == "Fix login bug"


@pytest.mark.asyncio
async def test_c_upper_copies_title_with_special_chars(tmp_path: Path):
    """'C' correctly copies titles with special characters and numbers."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(
        tasks_dir,
        [("implement-oauth2-flow", _TASK_TITLE_OAUTH2)],
    )

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("C")
            await pilot.pause()

            _, kwargs = _mock_subprocess_run.last_call
            assert kwargs["input"] == "Implement OAuth2 flow"


# ------ -------------------------- ------ ------------ ------ ----------- ----
# Test: Notification confirms what was copied
# ------ -------------------- ------ -------- ---- ---------- ------ ----------- ----


@pytest.mark.asyncio
async def test_copy_slug_shows_notification(tmp_path: Path):
    """Copying slug triggers a 'copied slug: …' notification."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("fix-login-bug", _TASK_SLUG_FIX_LOGIN)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("c")
            await pilot.pause()

            # Check notifications — Textual stores them in app._notifications
            notifications = [n.message for n in app._notifications]
            assert any("copied slug:" in msg for msg in notifications)


@pytest.mark.asyncio
async def test_copy_title_shows_notification(tmp_path: Path):
    """Copying title triggers a 'copied title: …' notification."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(
        tasks_dir,
        [("fix-login-bug", _TASK_SLUG_FIX_LOGIN)],
    )

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("C")
            await pilot.pause()

            notifications = [n.message for n in app._notifications]
            assert any("copied title:" in msg for msg in notifications)


@pytest.mark.asyncio
async def test_notification_confirms_copied_content(tmp_path: Path):
    """Notification message includes the actual copied value so the user knows what was sent."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("fix-login-bug", _TASK_SLUG_FIX_LOGIN)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            # Press 'c' for slug
            await pilot.press("c")
            await pilot.pause()

            notifications = [n.message for n in app._notifications]
            slug_msgs = [m for m in notifications if "copied slug:" in m]
            assert len(slug_msgs) >= 1
            assert "fix-login-bug" in slug_msgs[0]

    # Use a SECOND app instance for the title test to keep state clean
    _reset_mock()
    app2 = _make_app(tasks_dir)
    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app2.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            # Press 'C' for title
            await pilot.press("C")
            await pilot.pause()

            notifications = [n.message for n in app2._notifications]
            title_msgs = [m for m in notifications if "copied title:" in m]
            assert len(title_msgs) >= 1
            assert "Fix login bug" in title_msgs[0]


# ------ -------------------------- ------ ------------ ------ ----------- ----
# Test: Mock clipboard command is actually invoked
# ------ -------------------- ------ -------- ---- ---------- ------ ----------- ----


@pytest.mark.asyncio
async def test_subprocess_run_called_with_xclip_on_linux(tmp_path: Path):
    """On non-darwin systems the clipboard command uses xclip."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("fix-login-bug", _TASK_SLUG_FIX_LOGIN)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("c")
            await pilot.pause()

            args, kwargs = _mock_subprocess_run.last_call
            cmd = args[0] if args else kwargs.get("args", [])
            assert "xclip" in cmd


@pytest.mark.asyncio
async def test_text_true_passed_to_subprocess(tmp_path: Path):
    """subprocess.run is called with text=True so input is treated as a string."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("fix-login-bug", _TASK_SLUG_FIX_LOGIN)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("c")
            await pilot.pause()

            args, kwargs = _mock_subprocess_run.last_call
            assert kwargs.get("text") is True


@pytest.mark.asyncio
async def test_check_false_passed_to_subprocess(tmp_path: Path):
    """subprocess.run is called with check=False so a failed copy doesn't crash."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("fix-login-bug", _TASK_SLUG_FIX_LOGIN)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("c")
            await pilot.pause()

            args, kwargs = _mock_subprocess_run.last_call
            assert kwargs.get("check") is False


# ------ -------------------------- ------ ------------ ------ ----------- ----
# Test: Copy when no selection does nothing
# ------ -------------------- ------ -------- ---- ---------- ------ ----------- ----


@pytest.mark.asyncio
async def test_copy_with_no_task_selected_does_nothing(tmp_path: Path):
    """If no task is selected, pressing 'c' or 'C' should not call subprocess."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    # No tasks → nothing selected

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            await pilot.press("c")
            await pilot.pause()
            await pilot.press("C")
            await pilot.pause()

            # subprocess.run should never have been called because there is no selection
            assert _mock_subprocess_run.last_call is None


# ------ -------------------------- ------ ------------ ------ ----------- ----
# Test: Copy different tasks yields different content
# ------ -------------------- ------ -------- ---- ---------- ------ ----------- ----


@pytest.mark.asyncio
async def test_copy_different_tasks_yields_different_content(tmp_path: Path):
    """Selecting different tasks and copying produces different slug values."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(
        tasks_dir,
        [
            ("fix-login-bug", _TASK_SLUG_FIX_LOGIN),
            ("implement-oauth2-flow", _TASK_TITLE_OAUTH2),
        ],
    )

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            # First task is selected by default
            await pilot.press("c")
            await pilot.pause()

            slug_1 = _mock_subprocess_run.last_call[1]["input"]
            assert slug_1 == "fix-login-bug"
            _reset_mock()

            # Move to second task
            await pilot.press("down")
            await pilot.pause()

            await pilot.press("c")
            await pilot.pause()

            slug_2 = _mock_subprocess_run.last_call[1]["input"]
            assert slug_2 == "implement-oauth2-flow"

            assert slug_1 != slug_2


# ------ -------------------------- ------ ------------ ------ ----------- ----
# Test: 'c' and 'C' produce different clipboard data
# ------ -------------------- ------ -------- ---- ---------- ------ ----------- ----


@pytest.mark.asyncio
async def test_c_and_upper_c_produce_different_content(tmp_path: Path):
    """'c' (slug) and 'C' (title) copy different field values for the same task."""
    _reset_mock()

    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("implement-oauth2-flow", _TASK_TITLE_OAUTH2)])

    app = _make_app(tasks_dir)

    with mock.patch("board_tui.app.subprocess.run", side_effect=_mock_subprocess_run):
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()

            # 'c' → slug
            await pilot.press("c")
            await pilot.pause()
            slug = _mock_subprocess_run.last_call[1]["input"]
            assert slug == "implement-oauth2-flow"

            _reset_mock()

            # 'C' → title
            await pilot.press("C")
            await pilot.pause()
            title = _mock_subprocess_run.last_call[1]["input"]
            assert title == "Implement OAuth2 flow"

            assert slug != title
