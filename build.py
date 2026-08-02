#!/usr/bin/env python3
"""
Cannapedia static site generator
=================================

Reads Markdown articles (with YAML frontmatter) from content/articles/ and
standalone pages from content/pages/, renders them through Jinja2 templates
in templates/, and writes a fully static site to dist/.

Why this architecture
----------------------
- Content (Markdown + YAML) is completely decoupled from presentation
  (Jinja2 templates + CSS). That means the visual design can be reworked,
  or the renderer swapped for a real framework/CMS later, without
  touching a single article.
- The output of this script is plain static HTML/CSS/JS. That can be
  previewed locally with nothing but Python's built-in web server, and it
  can be deployed as-is to any static host (Netlify, Vercel, Cloudflare
  Pages, GitHub Pages, S3 + CloudFront, etc.) the moment you want
  Cannapedia to be a real, internet-accessible site.
- Clean, extension-less URLs (/wiki/<slug>/, /category/<slug>/) are
  generated now, so the URL structure won't need to change when this
  moves behind a real domain.
- If/when Cannapedia needs to be dynamic (user accounts, edit history,
  comments, a real "anyone can edit" model like Wikipedia), the natural
  next step is to put this same content model behind a small web
  framework (e.g. Flask/FastAPI) backed by a database -- the Markdown +
  frontmatter schema used here maps directly onto DB columns
  (title, short_description, categories, infobox, body, references),
  so migrating later is mechanical, not a rewrite.

Usage
-----
    python3 build.py

Then preview with:
    python3 serve.py
"""
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent.resolve()
ARTICLES_DIR = ROOT / "content" / "articles"
PAGES_DIR = ROOT / "content" / "pages"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
ADMIN_DIR = ROOT / "admin"
DIST_DIR = ROOT / "dist"

MD_EXTENSIONS = ["extra", "toc", "sane_lists", "smarty"]
MD_EXTENSION_CONFIG = {
    "toc": {"permalink": False, "toc_depth": "2-4"},
}


def cslug(name: str) -> str:
    """Turn a category name into a URL-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def read_frontmatter(path: Path):
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path} is missing YAML frontmatter (must start with '---').")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path} has malformed frontmatter.")
    _, fm_raw, body = parts
    meta = yaml.safe_load(fm_raw) or {}
    return meta, body


def render_markdown(body: str):
    md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_EXTENSION_CONFIG)
    html = md.convert(body)
    return html, getattr(md, "toc", "")


def load_article(path: Path) -> dict:
    meta, body = read_frontmatter(path)
    html, toc_html = render_markdown(body)

    plain_text = re.sub(r"<[^>]+>", " ", html)
    plain_text = re.sub(r"\s+", " ", plain_text).strip()
    word_count = len(plain_text.split())
    reading_minutes = max(1, round(word_count / 220))

    meta.setdefault("categories", [])
    meta.setdefault("infobox", [])
    meta.setdefault("references", [])
    meta.setdefault("widgets", [])
    meta.setdefault("status", "Article")

    meta.update(
        {
            "slug": path.stem,
            "html": html,
            "toc_html": toc_html,
            "word_count": word_count,
            "reading_minutes": reading_minutes,
            "plain_text": plain_text,
        }
    )
    return meta


def load_page(path: Path) -> dict:
    meta, body = read_frontmatter(path)
    html, _ = render_markdown(body)
    meta.update({"slug": path.stem, "html": html})
    return meta


def resolve_related_widgets(articles: list) -> None:
    """For any 'related' widget, turn a list of article slugs into the
    title/description pairs the template needs, looked up from the other
    loaded articles. Keeps article frontmatter terse (just slugs) while
    staying correct if a linked article's title ever changes."""
    by_slug = {a["slug"]: a for a in articles}
    for a in articles:
        for w in a.get("widgets") or []:
            if w.get("type") == "related":
                resolved = []
                for s in w.get("items", []):
                    target = by_slug.get(s)
                    if target:
                        resolved.append(
                            {
                                "slug": s,
                                "title": target["title"],
                                "short_description": target.get("short_description", ""),
                            }
                        )
                w["resolved_items"] = resolved


VALID_STATUSES = {"Stub", "Article", "Featured article"}
VALID_WIDGET_TYPES = {"trivia", "quote", "timeline", "related", "factbox"}
TABLE_WIDGET_TYPES = {"timeline", "factbox"}


def validate_articles(articles: list) -> tuple:
    """Sanity-check the loaded articles before anything gets written out.

    Returns (errors, warnings). Errors describe things that would render
    broken or misleading pages (a dangling "related" link, a malformed
    widget row, two articles fighting over one URL) and should block a
    build. Warnings are just missing polish (no short description, no
    categories) -- worth flagging in the build log, not worth blocking a
    publish over.
    """
    errors = []
    warnings = []
    seen_slugs = {}
    by_slug = {a["slug"]: a for a in articles}

    for a in articles:
        label = f"\"{a.get('title') or a['slug']}\" ({a['slug']})"

        if a["slug"] in seen_slugs:
            errors.append(
                f"{label}: slug is already used by {seen_slugs[a['slug']]} -- "
                f"two articles can't share one URL."
            )
        else:
            seen_slugs[a["slug"]] = label

        if not (a.get("title") or "").strip():
            errors.append(f"{a['slug']}: missing a title.")
        if not (a.get("short_description") or "").strip():
            warnings.append(f"{label}: no short_description set.")
        if not a.get("categories"):
            warnings.append(f"{label}: no categories set.")

        status = a.get("status")
        if status not in VALID_STATUSES:
            warnings.append(
                f"{label}: status \"{status}\" isn't one of {sorted(VALID_STATUSES)}."
            )

        for row in a.get("infobox") or []:
            if not isinstance(row, dict) or not row.get("label") or "value" not in row:
                errors.append(f"{label}: infobox row is missing a label/value: {row!r}")

        for w in a.get("widgets") or []:
            wtype = w.get("type")
            if wtype not in VALID_WIDGET_TYPES:
                errors.append(
                    f"{label}: widget has an unknown type {wtype!r} "
                    f"(expected one of {sorted(VALID_WIDGET_TYPES)})."
                )
                continue
            if wtype in TABLE_WIDGET_TYPES:
                for row in w.get("items") or []:
                    if not isinstance(row, dict) or not row.get("label") or "value" not in row:
                        errors.append(
                            f"{label}: {wtype} widget row is missing a label/value: {row!r}"
                        )
            if wtype == "related":
                for s in w.get("items") or []:
                    if s not in by_slug:
                        errors.append(
                            f"{label}: \"related\" widget links to \"{s}\", "
                            f"which isn't the slug of any existing article."
                        )
            if wtype == "quote" and not (w.get("text") or "").strip():
                errors.append(f"{label}: quote widget has no quote text.")

    return errors, warnings


def build():
    articles = sorted(
        (load_article(p) for p in ARTICLES_DIR.glob("*.md")),
        key=lambda a: a["title"],
    )
    pages = [load_page(p) for p in PAGES_DIR.glob("*.md")] if PAGES_DIR.exists() else []
    resolve_related_widgets(articles)

    # Validate before touching dist/ at all, so a bad article can never
    # half-overwrite a previously-good build.
    errors, warnings = validate_articles(articles)
    for w in warnings:
        print(f"[warning] {w}")
    if errors:
        print(f"\n[FAILED] {len(errors)} problem(s) found, nothing was published:")
        for e in errors:
            print(f"  - {e}")
        print(
            "\nFix these in the article (or in the CMS) and save/preview again. "
            "dist/ was left untouched, so the live site is unaffected."
        )
        raise SystemExit(1)

    # Rebuild idempotently: try a clean wipe of dist/, but don't require it.
    # Some environments (locked files, certain sync/network filesystems)
    # refuse deletes even though writes are fine, so we fall back to
    # overwriting files in place rather than failing the whole build.
    if DIST_DIR.exists():
        try:
            shutil.rmtree(DIST_DIR)
        except OSError:
            pass
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, DIST_DIR / "static", dirs_exist_ok=True)

    # The Decap CMS editor panel (content/tags/etc. management for
    # non-technical contributors) lives at /admin on the same deployed site.
    if ADMIN_DIR.exists():
        shutil.copytree(ADMIN_DIR, DIST_DIR / "admin", dirs_exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["cslug"] = cslug

    categories = {}
    for a in articles:
        for c in a.get("categories", []):
            categories.setdefault(c, []).append(a)
    category_names = sorted(categories.keys())

    common_ctx = {
        "all_articles": articles,
        "categories": category_names,
        "site_article_count": len(articles),
        "build_date": date.today().isoformat(),
    }

    article_tpl = env.get_template("article.html")
    for a in articles:
        out_dir = DIST_DIR / "wiki" / a["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(
            article_tpl.render(article=a, **common_ctx), encoding="utf-8"
        )

    category_tpl = env.get_template("category.html")
    for name, items in categories.items():
        out_dir = DIST_DIR / "category" / cslug(name)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(
            category_tpl.render(category=name, category_articles=items, **common_ctx),
            encoding="utf-8",
        )

    page_tpl = env.get_template("page.html")
    for p in pages:
        out_dir = DIST_DIR / p["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(
            page_tpl.render(page=p, **common_ctx), encoding="utf-8"
        )

    index_tpl = env.get_template("index.html")
    (DIST_DIR / "index.html").write_text(
        index_tpl.render(**common_ctx), encoding="utf-8"
    )

    # 404 page (useful locally and on most static hosts)
    if (TEMPLATES_DIR / "404.html").exists():
        notfound_tpl = env.get_template("404.html")
        (DIST_DIR / "404.html").write_text(
            notfound_tpl.render(**common_ctx), encoding="utf-8"
        )

    search_index = [
        {
            "title": a["title"],
            "slug": a["slug"],
            "short_description": a.get("short_description", ""),
            "url": f"/wiki/{a['slug']}/",
            "categories": a.get("categories", []),
            "text": a["plain_text"][:20000],
        }
        for a in articles
    ]
    (DIST_DIR / "search-index.json").write_text(
        json.dumps(search_index, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Built {len(articles)} article(s), "
          f"{len(category_names)} categor{'y' if len(category_names)==1 else 'ies'}, "
          f"{len(pages)} page(s) -> {DIST_DIR}")


if __name__ == "__main__":
    build()
