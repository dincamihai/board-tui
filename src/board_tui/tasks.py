"""Pure functions for reading/writing .tasks/*.md files."""

import re
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
COMMENTS_RE = re.compile(r"\n## Comments\n(.*?)(?=\n## |\Z)", re.DOTALL)
COMMENT_ITEM_RE = re.compile(r"^- \*\*([^@]+) @([^:]+)\*\*: (.+)$", re.MULTILINE)


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s[:70]


def parse(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    fm, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
        body = m.group(2).lstrip("\n")
    return fm, body


def dump(path: Path, fm: dict, body: str) -> None:
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    lines.append(body.rstrip() + "\n")
    path.write_text("\n".join(lines))


def load_tasks(tasks_dir: Path, columns: list[str]) -> list[dict]:
    if not tasks_dir.exists():
        return []
    out = []
    for p in sorted(tasks_dir.glob("*.md")):
        fm, body = parse(p)
        title = ""
        for line in body.splitlines():
            if line.strip().startswith("#"):
                title = line.lstrip("#").strip()
                break
        if not title:
            title = p.stem
        try:
            order = int(fm.get("order", "1000"))
        except ValueError:
            order = 1000
        out.append({
            "slug": p.stem, "path": p, "column": fm.get("column", columns[0]),
            "title": title, "order": order, "fm": fm, "body": body,
        })
    out.sort(key=lambda t: (t["order"], t["slug"]))
    return out


def mine(task: dict, user: str) -> bool:
    return (
        task["fm"].get("assigned", "").lower() == user.lower()
        or task["title"].startswith("[human]")
    )


def extract_comments(body: str) -> list[dict]:
    """Extract comments from task body.

    Returns list of {date, author, text} dicts.
    Strips Comments section from body for separate rendering.
    """
    match = COMMENTS_RE.search(body)
    if not match:
        return []

    comments_text = match.group(1)
    comments = []

    for line in comments_text.strip().split("\n"):
        m = COMMENT_ITEM_RE.match(line.strip())
        if m:
            comments.append({
                "date": m.group(1).strip(),
                "author": m.group(2).strip(),
                "text": m.group(3).strip(),
            })

    return comments


def strip_comments_section(body: str) -> str:
    """Remove Comments section from body for clean display."""
    return COMMENTS_RE.sub("", body).rstrip()


def add_comment(path: Path, author: str, text: str, date: str) -> None:
    """Add a comment to a task file.

    Creates Comments section if missing, otherwise appends.
    """
    fm, body = parse(path)
    comments = extract_comments(body)
    body_without_comments = strip_comments_section(body)

    comment_line = f"- **{date} @{author}**: {text}\n"

    if comments:
        # Append to existing Comments section
        match = COMMENTS_RE.search(body)
        if match:
            new_comments = body_without_comments + "\n\n## Comments\n"
            for c in comments:
                new_comments += f"- **{c['date']} @{c['author']}**: {c['text']}\n"
            new_comments += comment_line
            body = new_comments
    else:
        # Create new Comments section
        body = body_without_comments + "\n\n## Comments\n" + comment_line

    dump(path, fm, body)
