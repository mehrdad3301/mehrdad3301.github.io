#!/usr/bin/env python3
"""Build blog HTML from Markdown files in posts/.

Write a post as posts/my-title.md:

    ---
    title: The title
    date: 2026-10-15
    summary: One or two sentences for the blog index.
    ---

    The body is Markdown. Images can use paths from the repo root,
    such as assets/photo.png.

Set draft: true to keep a post out of the build.

    python3 scripts/build_blog.py

The first run creates .venv and installs the Markdown package there.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def venv_has_markdown() -> bool:
    if not VENV_PYTHON.exists():
        return False
    probe = subprocess.run(
        [str(VENV_PYTHON), "-c", "import markdown"],
        capture_output=True,
    )
    return probe.returncode == 0


def ensure_markdown():
    try:
        import markdown
    except ImportError:
        if not venv_has_markdown():
            if not VENV_PYTHON.exists():
                subprocess.check_call([sys.executable, "-m", "venv", ROOT / ".venv"])
            subprocess.check_call([str(VENV_PYTHON), "-m", "pip", "install", "markdown>=3.5"])
        os_exec()
    return markdown


def os_exec():
    import os

    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__, *sys.argv[1:]])


markdown = ensure_markdown()

POSTS_DIR = ROOT / "posts"
BLOG_DIR = ROOT / "blog"
LEDE = "Notes on things I am trying to understand."

FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=IBM+Plex+Serif:ital,wght@0,400;0,700;1,400;1,700&amp;display=swap"
)

MD = markdown.Markdown(
    extensions=["fenced_code", "tables", "smarty", "sane_lists", "footnotes"],
    output_format="html",
)


def rel(path: str) -> str:
    return "../" + path


def parse_post(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        sys.exit(f"{path.name}: missing front matter")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        sys.exit(f"{path.name}: front matter was not closed")
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            sys.exit(f"{path.name}: bad front matter line: {line}")
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip()
    if "title" not in meta or "date" not in meta:
        sys.exit(f"{path.name}: title and date are required")
    try:
        published = date.fromisoformat(meta["date"])
    except ValueError:
        sys.exit(f"{path.name}: date must be YYYY-MM-DD")
    slug = path.stem
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        sys.exit(f"{path.name}: use a lowercase hyphenated file name")
    return {
        "title": meta["title"],
        "date": published,
        "summary": meta.get("summary", ""),
        "draft": meta.get("draft", "").lower() in {"true", "yes", "1"},
        "slug": slug,
        "body": parts[2].strip() + "\n",
        "source": path.name,
    }


def load_posts() -> list[dict]:
    if not POSTS_DIR.exists():
        return []
    posts = []
    seen: set[str] = set()
    for path in sorted(POSTS_DIR.glob("*.md")):
        post = parse_post(path)
        if post["draft"]:
            continue
        if post["slug"] in seen:
            sys.exit(f"Two posts use the slug {post['slug']}")
        seen.add(post["slug"])
        posts.append(post)
    posts.sort(key=lambda post: (post["date"], post["slug"]), reverse=True)
    return posts


def render_body(source: str) -> str:
    MD.reset()
    rendered = MD.convert(source)
    return rendered.replace('src="assets/', 'src="../assets/')


def format_date(published: date) -> str:
    return f"{published:%B} {published.day}, {published.year}"


def shell(title: str, description: str, main: str, current: str) -> str:
    home_current = ' aria-current="page"' if current == "home" else ""
    blog_current = ' aria-current="page"' if current == "blog" else ""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f8f8f8">
  <title>__TITLE__</title>
  <meta name="description" content="__DESCRIPTION__">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="__FONTS__" rel="stylesheet">
  <link rel="stylesheet" href="__CSS__">
</head>
<body>
  <a class="skip" href="#content">Skip to content</a>
  <div class="page">
    <nav class="site-nav" aria-label="Site">
      <a href="__HOME__"__HOME_CURRENT__>Home</a>
      <a href="__BLOG__"__BLOG_CURRENT__>Blog</a>
    </nav>
    <main id="content" class="prose">
__MAIN__
    </main>
  </div>
</body>
</html>
"""
    return (
        template.replace("__TITLE__", html.escape(title))
        .replace("__DESCRIPTION__", html.escape(description))
        .replace("__FONTS__", FONTS)
        .replace("__CSS__", rel("style.css"))
        .replace("__HOME__", rel("index.html"))
        .replace("__BLOG__", "index.html")
        .replace("__HOME_CURRENT__", home_current)
        .replace("__BLOG_CURRENT__", blog_current)
        .replace("__MAIN__", main)
    )


def render_index(posts: list[dict]) -> str:
    if posts:
        items = []
        for post in posts:
            summary = f"\n        <p>{html.escape(post['summary'])}</p>" if post["summary"] else ""
            items.append(
                "      <li>\n"
                f'        <p class="post-date">{format_date(post["date"])}</p>\n'
                '        <h2><a href="'
                + html.escape(post["slug"])
                + '.html">'
                + html.escape(post["title"])
                + "</a></h2>"
                + summary
                + "\n      </li>"
            )
        listing = "\n    <ul class=\"post-list\">\n" + "\n".join(items) + "\n    </ul>"
    else:
        listing = ""
    main = (
        '    <h1 class="page-title">Blog</h1>\n'
        f'    <p class="lede">{html.escape(LEDE)}</p>{listing}'
    )
    return shell("Blog — Mehrdad Aksari Mahabadi", LEDE, main, "blog")


def render_post(post: dict) -> str:
    description = post["summary"] or post["title"]
    main = (
        "    <article>\n"
        f'      <p class="post-date">{format_date(post["date"])}</p>\n'
        "      <h1>" + html.escape(post["title"]) + "</h1>\n"
        "      " + render_body(post["body"]) + "\n"
        "    </article>\n"
        '    <p class="back"><a href="index.html">All posts</a></p>'
    )
    title = f"{post['title']} — Mehrdad Aksari Mahabadi"
    return shell(title, description, main, "blog")


def main() -> None:
    posts = load_posts()
    BLOG_DIR.mkdir(exist_ok=True)
    keep = {"index.html"}
    (BLOG_DIR / "index.html").write_text(render_index(posts), encoding="utf-8")
    for post in posts:
        name = f"{post['slug']}.html"
        keep.add(name)
        (BLOG_DIR / name).write_text(render_post(post), encoding="utf-8")
    for stale in BLOG_DIR.glob("*.html"):
        if stale.name not in keep:
            stale.unlink()
    print(f"Built {len(posts)} post{'s' if len(posts) != 1 else ''} into {BLOG_DIR}")


if __name__ == "__main__":
    main()
