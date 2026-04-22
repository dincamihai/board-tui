"""Textual-based TUI kanban board."""

import datetime as dt
import os
import platform
import subprocess
from pathlib import Path

from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Footer, Header, Input, ListItem, ListView, Label, Markdown,
)

from board_tui.tasks import dump, load_tasks, mine, slugify


class PromptScreen(ModalScreen[str]):
    CSS = "#prompt { width: 60%; padding: 1 2; border: round $accent; }"

    def __init__(self, label: str):
        super().__init__()
        self.label = label

    def compose(self) -> ComposeResult:
        with Vertical(id="prompt"):
            yield Label(self.label)
            yield Input(id="prompt-input")

    def on_mount(self):
        self.query_one(Input).focus()

    def on_input_submitted(self, ev: Input.Submitted):
        self.dismiss(ev.value)

    def on_key(self, ev: events.Key):
        if ev.key == "escape":
            self.dismiss(None)


class BoardApp(App):
    CSS = """
    Screen { layout: horizontal; }
    #board { width: 60%; layout: horizontal; padding: 0 1; }
    .column { width: 1fr; height: 100%; padding: 0 1; }
    .column-title { text-style: bold; color: $accent; padding: 0 1; }
    .column-title-active { text-style: bold reverse; color: $accent; padding: 0 1; }
    ListView { height: 1fr; border: round $primary-darken-2; }
    ListView:focus { border: round $accent; }
    ListItem { padding: 0 1; }
    ListItem.mine { color: cyan; text-style: dim; }
    ListItem.matched { text-style: bold; }
    ListItem.indent-1 { padding-left: 2; }
    #detail { width: 40%; padding: 0 1; border-left: solid $primary-darken-2; }
    #detail-header { text-style: bold reverse; padding: 0 1; }
    #detail-scroll { height: 1fr; }
    #detail-scroll:focus { border: round $accent; }
    #detail-body { height: auto; }
    Input { dock: bottom; }
    """

    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("tab", "focus_next_pane", "switch pane", priority=True),
        Binding("a", "add_card", "add"),
        Binding("/", "search", "search"),
        Binding("n", "next_match", "next match"),
        Binding("escape", "escape", "cancel/clear"),
        Binding("c", "copy_slug", "copy slug"),
        Binding("C", "copy_title", "copy title"),
        Binding("m", "toggle_move", "move"),
        Binding("enter", "toggle_move", "move"),
        Binding("r", "refresh", "refresh"),
        Binding("d", "delegate_task", "delegate"),
        Binding("D", "cancel_delegation", "cancel delegation"),
        Binding("space", "toggle_collapse", "collapse/expand"),
    ]

    move_mode = reactive(False)
    search_query = reactive("")
    focus_side = reactive("board")

    def __init__(self, tasks_dir: str | None = None, columns: list[str] | None = None, user: str | None = None):
        super().__init__()
        self._tasks_dir = Path(tasks_dir) if tasks_dir else Path(os.getcwd()) / ".tasks"
        self._columns = columns or ["Backlog", "In Progress", "Done"]
        self._user = user or os.environ.get("USER", "unknown")
        self.cur_col = 0
        self.tasks = []
        self.by_col = {c: [] for c in self._columns}
        self.search_matches = []
        self.search_pos = 0
        self._collapsed_parents: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="board"):
            for col in self._columns:
                with Vertical(classes="column", id=f"col-{slugify(col)}"):
                    yield Label(f" {col} ", classes="column-title",
                                id=f"title-{slugify(col)}")
                    yield ListView(id=f"list-{slugify(col)}")
        with Vertical(id="detail"):
            yield Label("DETAIL", id="detail-header")
            with VerticalScroll(id="detail-scroll"):
                yield Markdown("", id="detail-body")
        yield Footer()

    def on_mount(self):
        self._reload()
        self._focus_column(0)

    def _reload(self):
        self.tasks = load_tasks(self._tasks_dir, self._columns)
        all_slugs = {t["slug"] for t in self.tasks}
        self.by_col = {c: [] for c in self._columns}
        for t in self.tasks:
            self.by_col.setdefault(t["column"], []).append(t)

        # Per-column: compute children from flat list, reorder, render
        self._children_by_col = {}
        for col in self._columns:
            flat_tasks = self.by_col[col]
            # Map parent slug -> children in this column (from flat list)
            children_by_parent: dict[str, list] = {}
            for t in flat_tasks:
                parent = t["fm"].get("parent")
                if parent and parent in all_slugs and any(p["slug"] == parent for p in flat_tasks):
                    children_by_parent.setdefault(parent, []).append(t)
            self._children_by_col[col] = children_by_parent

            # Reorder: parent, visible children (recursive), standalone
            ordered = []
            used = set()

            def add_with_children(task):
                if task["slug"] in used:
                    return
                ordered.append(task)
                used.add(task["slug"])
                if task["slug"] not in self._collapsed_parents:
                    for child in children_by_parent.get(task["slug"], []):
                        add_with_children(child)

            for t in flat_tasks:
                if t["slug"] in used:
                    continue
                parent = t["fm"].get("parent")
                if parent and parent in all_slugs and any(p["slug"] == parent for p in flat_tasks):
                    continue
                add_with_children(t)

            self.by_col[col] = ordered

        def _restore_col_index(lv, prev_idx, col_name):
            n = len(self.by_col.get(col_name, []))
            if prev_idx < n:
                lv.index = prev_idx
            else:
                lv.index = max(0, n - 1)

        for col in self._columns:
            lv = self.query_one(f"#list-{slugify(col)}", ListView)
            prev_idx = lv.index or 0
            lv.clear()
            col_tasks = self.by_col[col]
            children_by_parent = self._children_by_col.get(col, {})

            for t in col_tasks:
                label_text = t["title"]
                parent = t["fm"].get("parent")
                is_parent = t["slug"] in children_by_parent
                is_child = parent and parent in all_slugs and any(p["slug"] == parent for p in col_tasks)
                is_orphan = parent and parent not in all_slugs

                prefix = "♦ " if mine(t, self._user) else "• "
                ds = t["fm"].get("delegation_status")
                if ds == "queued":
                    prefix = "⏳ "
                elif ds == "processing":
                    prefix = "▶ "
                elif ds == "done":
                    prefix = "✓ "

                indent = 0
                classes = []

                if is_orphan:
                    prefix = "! " + prefix
                    label_text = f"{label_text}  ↑{parent}"
                elif is_child:
                    indent = 1
                    classes.append("indent-1")
                elif parent and not is_child:
                    label_text = f"{label_text}  ↑{parent}"

                if is_parent:
                    count = len(children_by_parent.get(t["slug"], []))
                    collapsed = t["slug"] in self._collapsed_parents
                    indicator = "▸" if collapsed else "▾"
                    label_text = f"{indicator}{count} {label_text}"

                matched = (
                    self.search_query
                    and (self.search_query.lower() in t["title"].lower()
                         or self.search_query.lower() in t["slug"].lower())
                )
                if mine(t, self._user):
                    classes.append("mine")
                if matched:
                    classes.append("matched")
                if is_orphan:
                    classes.append("orphan")

                item = ListItem(Label(prefix + label_text),
                                classes=" ".join(classes) if classes else "")
                item.data = t
                lv.append(item)

            self.call_after_refresh(_restore_col_index, lv, prev_idx, col)
        self._update_titles()
        self._update_detail()
        if self.focus_side == "board":
            col = self._columns[self.cur_col]
            self.query_one(f"#list-{slugify(col)}", ListView).focus()

    def _update_titles(self):
        for i, col in enumerate(self._columns):
            lbl = self.query_one(f"#title-{slugify(col)}", Label)
            n = len(self.by_col.get(col, []))
            text = f" {col} ({n}) "
            if i == self.cur_col and self.focus_side == "board":
                lbl.add_class("column-title-active")
                lbl.remove_class("column-title")
            else:
                lbl.add_class("column-title")
                lbl.remove_class("column-title-active")
            lbl.update(text)

    def _update_detail(self):
        sel = self._selected()
        header = self.query_one("#detail-header", Label)
        body = self.query_one("#detail-body", Markdown)
        prefix = "▾ " if self.focus_side == "detail" else ""
        if self.move_mode:
            header.update(f" MOVE · arrows relocate · enter/esc done ")
        else:
            header.update(f" {prefix}DETAIL ")
        if not sel:
            body.update("_no selection_")
            return
        all_slugs = {t["slug"] for t in self.tasks}
        md = [f"### {sel['title']}", "", f"`{sel['slug']}` · _{sel['column']}_"]
        for k, v in sel["fm"].items():
            if k == "column":
                continue
            if k == "parent":
                parent_slug = v
                if parent_slug not in all_slugs:
                    md.append(f"- **{k}**: {v} ⚠️ _(not found)_")
                    md.append("")
                    md.append(f"> This task references parent `{parent_slug}` which does not exist.")
                    md.append("> Consider updating the `parent` frontmatter or creating the parent task.")
                    continue
            md.append(f"- **{k}**: {v}")
        md.append("")
        md.append(sel["body"])
        body.update("\n".join(md))

    def _selected(self):
        col = self._columns[self.cur_col]
        items = self.by_col.get(col, [])
        lv = self.query_one(f"#list-{slugify(col)}", ListView)
        idx = lv.index if lv.index is not None else 0
        if 0 <= idx < len(items):
            return items[idx]
        return None

    def _focus_column(self, idx):
        idx = idx % len(self._columns)
        self.cur_col = idx
        col = self._columns[idx]
        lv = self.query_one(f"#list-{slugify(col)}", ListView)
        lv.focus()
        self._update_titles()
        self._update_detail()

    def action_focus_next_pane(self):
        if self.focus_side == "board":
            self.focus_side = "detail"
            self.query_one("#detail-scroll", VerticalScroll).focus()
        else:
            self.focus_side = "board"
            self._focus_column(self.cur_col)
        self._update_titles()
        self._update_detail()

    def action_toggle_move(self):
        if self.focus_side != "board":
            return
        if not self._selected():
            return
        self.move_mode = not self.move_mode
        self._update_detail()

    def action_toggle_collapse(self):
        if self.focus_side != "board":
            return
        sel = self._selected()
        if not sel:
            return
        col = self._columns[self.cur_col]
        children_by_parent = self._children_by_col.get(col, {})
        if sel["slug"] not in children_by_parent:
            return
        if sel["slug"] in self._collapsed_parents:
            self._collapsed_parents.remove(sel["slug"])
        else:
            self._collapsed_parents.add(sel["slug"])
        self._reload()

    _clipboard_cmd = ["pbcopy"] if platform.system() == "Darwin" else ["xclip", "-selection", "clipboard"]

    def action_copy_slug(self):
        sel = self._selected()
        if not sel:
            return
        subprocess.run(self._clipboard_cmd, input=sel["slug"], text=True, check=False)
        self.notify(f"copied slug: {sel['slug']}")

    def action_copy_title(self):
        sel = self._selected()
        if not sel:
            return
        subprocess.run(self._clipboard_cmd, input=sel["title"], text=True, check=False)
        self.notify(f"copied title: {sel['title']}")

    def action_refresh(self):
        self._reload()
        self.notify("refreshed")

    def action_delegate_task(self):
        if self.focus_side != "board":
            return
        sel = self._selected()
        if not sel:
            return
        col = sel["column"]
        if col not in ("Backlog", "In Progress"):
            self.notify(f"cannot delegate from {col}")
            return
        sel["fm"]["delegation_status"] = "queued"
        dump(sel["path"], sel["fm"], sel["body"])
        self._reload()
        self.notify(f"delegated {sel['slug']}")

    def action_cancel_delegation(self):
        if self.focus_side != "board":
            return
        sel = self._selected()
        if not sel:
            return
        ds = sel["fm"].get("delegation_status")
        if ds not in ("queued", "processing"):
            return
        sel["fm"]["delegation_status"] = "cancelled"
        dump(sel["path"], sel["fm"], sel["body"])
        self._reload()
        self.notify(f"cancelled {sel['slug']}")

    def action_escape(self):
        if self.move_mode:
            self.move_mode = False
            self._update_detail()
            return
        if self.search_query:
            self.search_query = ""
            self.search_matches = []
            self._reload()
            return

    def action_search(self):
        self.push_screen(PromptScreen("search:"), self._on_search)

    def _on_search(self, raw: str | None):
        if raw is None:
            return
        self.search_query = raw.strip()
        self.search_matches = []
        if self.search_query:
            q = self.search_query.lower()
            for i2, col2 in enumerate(self._columns):
                for j2, t2 in enumerate(self.by_col.get(col2, [])):
                    if q in t2["title"].lower() or q in t2["slug"].lower():
                        self.search_matches.append((i2, j2))
            if self.search_matches:
                self.search_pos = 0
                ci, ri = self.search_matches[0]
                self._focus_column(ci)
                self.query_one(
                    f"#list-{slugify(self._columns[ci])}", ListView
                ).index = ri
                self.notify(f"{len(self.search_matches)} matches")
            else:
                self.notify(f"no matches for '{self.search_query}'")
        self._reload()

    def action_next_match(self):
        if not self.search_matches:
            return
        self.search_pos = (self.search_pos + 1) % len(self.search_matches)
        ci, ri = self.search_matches[self.search_pos]
        self._focus_column(ci)
        self.query_one(
            f"#list-{slugify(self._columns[ci])}", ListView
        ).index = ri
        self.notify(f"match {self.search_pos + 1}/{len(self.search_matches)}")

    def action_add_card(self):
        self.push_screen(PromptScreen("new task title:"), self._on_add)

    def _on_add(self, raw: str | None):
        if not raw:
            return
        slug = slugify(raw)
        self._tasks_dir.mkdir(exist_ok=True)
        path = self._tasks_dir / f"{slug}.md"
        if path.exists():
            self.notify(f"'{slug}' already exists")
            return
        dump(path, {
            "column": self._columns[self.cur_col],
            "created": dt.date.today().isoformat(),
        }, f"# {raw}\n")
        self.notify(f"created {slug}")
        self._reload()

    def on_key(self, event: events.Key):
        if self.focus_side == "detail":
            return
        sel = self._selected()
        if self.move_mode and sel:
            if event.key == "right":
                new_col = self._columns[(self.cur_col + 1) % len(self._columns)]
                sel["fm"]["column"] = new_col
                sel["fm"]["updated"] = dt.datetime.now(
                    dt.timezone.utc
                ).isoformat(timespec="seconds")
                dump(sel["path"], sel["fm"], sel["body"])
                self.cur_col = (self.cur_col + 1) % len(self._columns)
                self._reload()
                self._focus_column(self.cur_col)
                event.stop()
                return
            if event.key == "left":
                new_col = self._columns[(self.cur_col - 1) % len(self._columns)]
                sel["fm"]["column"] = new_col
                sel["fm"]["updated"] = dt.datetime.now(
                    dt.timezone.utc
                ).isoformat(timespec="seconds")
                dump(sel["path"], sel["fm"], sel["body"])
                self.cur_col = (self.cur_col - 1) % len(self._columns)
                self._reload()
                self._focus_column(self.cur_col)
                event.stop()
                return
            if event.key in ("up", "down"):
                col_items = self.by_col.get(self._columns[self.cur_col], [])
                lv = self.query_one(
                    f"#list-{slugify(self._columns[self.cur_col])}", ListView
                )
                idx = lv.index or 0
                other = idx - 1 if event.key == "up" else idx + 1
                if 0 <= other < len(col_items):
                    a = col_items[idx]
                    b = col_items[other]
                    if a["order"] == b["order"]:
                        for i2, it in enumerate(col_items):
                            it["fm"]["order"] = str(i2 * 10)
                            dump(it["path"], it["fm"], it["body"])
                        a["order"] = idx * 10
                        b["order"] = other * 10
                    a["fm"]["order"], b["fm"]["order"] = str(b["order"]), str(a["order"])
                    dump(a["path"], a["fm"], a["body"])
                    dump(b["path"], b["fm"], b["body"])
                    self._reload()
                    lv.index = other
                event.stop()
                return
        if self.focus_side == "board":
            if event.key == "right":
                self._focus_column(self.cur_col + 1)
                event.stop()
                return
            if event.key == "left":
                self._focus_column(self.cur_col - 1)
                event.stop()
                return

    @on(ListView.Highlighted)
    def _on_highlight(self, event: ListView.Highlighted):
        self._update_detail()
