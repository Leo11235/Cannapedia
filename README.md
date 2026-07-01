# Cannapedia

Cannapedia is a Wikipedia-style encyclopedia about cannabis: history, science, culture, law, and the people who shaped it. This repo is a small static-site generator plus the first two articles.

## Quick start (one command)

From inside this folder:

```
python3 serve.py
```

This builds the site and starts a local server at **http://localhost:8000/** (it should also open automatically in your browser). Press `Ctrl+C` to stop it.

If port 8000 is already taken: `python3 serve.py --port 8001`

### Do I need to install anything?

Cannapedia only needs Python 3 plus three small, common libraries: `markdown`, `Jinja2`, and `PyYAML`. If `python3 serve.py` complains about a missing module, install them with:

```
pip install -r requirements.txt
```

(add `--break-system-packages` on some Linux systems if pip refuses to install globally). No Node.js, npm, or any other toolchain is required.

## What's actually in this project

```
content/
  articles/        one Markdown file per encyclopedia article
  pages/           standalone pages (About, etc.)
templates/         Jinja2 HTML templates (header, article layout, homepage, category page...)
static/
  css/style.css    the Wikipedia-inspired look
  js/search.js     client-side search + "Random article"
build.py            reads content/, renders templates, writes dist/
serve.py             runs build.py, then serves dist/ locally
dist/                generated output (not checked in; safe to delete any time)
```

Each article is a Markdown file with a YAML "frontmatter" header on top, e.g.:

```markdown
---
title: "History of Cannabis"
short_description: "..."
categories: [History, Archaeology]
infobox:
  - ["Earliest fiber use", "~12,000 years BP"]
references via footnotes: see the [^1] style markers in the body
---
Article text goes here, using normal Markdown...
```

To add a new article, drop a new `.md` file into `content/articles/`, give it the same frontmatter shape as the existing two, and re-run `python3 build.py` (or `serve.py`). It will automatically show up on the homepage, in its categories, and in search — no other code changes needed.

## Why it's built this way (and how this becomes a real website)

This project is deliberately a **plain static site generator** rather than a JavaScript framework, for two practical reasons:

1. **No install friction today.** The sandbox/network this was built in blocks the npm registry, so an Astro/Next.js/React setup couldn't actually be installed or tested here. Python with these libraries is reliable and almost certainly already on your machine.
2. **The easiest possible path to a real, internet-hosted website.** `python3 build.py` produces a `dist/` folder of plain HTML/CSS/JS with no server-side logic. That folder can be deployed *as-is*, today, to any static host — Netlify, Vercel, Cloudflare Pages, GitHub Pages, or a basic S3 bucket — typically by just dragging the `dist/` folder into the host's dashboard or pointing a `git push` deploy at this repo. There is nothing to "convert" later.

A few specific choices that keep the door open for growth:

- **Clean URLs** (`/wiki/<slug>/`, `/category/<slug>/`) are generated now, so the URL structure won't need to change when this gets a real domain.
- **Content is fully decoupled from presentation.** Articles are Markdown + YAML, independent of the HTML templates and CSS. If you outgrow this generator and want a real "anyone can edit" wiki (user accounts, edit history, revision diffs — like actual Wikipedia/MediaWiki), the natural next step is to put a small web framework (Flask/FastAPI/Django) and a database in front of this same content model. The frontmatter fields here (title, short_description, categories, infobox, references, body) map directly onto database columns, so migrating is mechanical rather than a rewrite.
- **Search is a placeholder, not a dead end.** `static/js/search.js` does simple client-side filtering over a generated `search-index.json`. That's fine for a handful of articles; when the article count grows, swap it for a real search tool (e.g., Pagefind, which builds a static search index with no backend, or a hosted service like Meilisearch/Algolia) without touching the rest of the site.
- **No vendor lock-in.** Nothing here depends on a specific host, framework, or paid service.

## Content so far

- **History of Cannabis** — archaeology and earliest evidence, ancient China/India/Egypt/the Near East, the Scythians, Greece and Rome, the Islamic world and hashish, Sub-Saharan Africa, medieval and colonial hemp, Western medicine, 20th-century prohibition and the War on Drugs, the discovery of THC and the endocannabinoid system, the modern legalization wave, and religion/culture/economics.
- **Frenchy Cannoli** — biography of the French-American hashishin (1956–2021): his apprenticeship across Morocco, Lebanon, Afghanistan, and the Himalayas, his life in California, his hash-making philosophy and "Lost Art of the Hashishin" workshops, his role in the California Cannabis Appellations movement, and his legacy.

Both articles are written with inline citations (numbered footnotes linking to source articles) in the same style as Wikipedia references.

## Disclaimer

Cannapedia is a demonstration/educational project and is not affiliated with Wikipedia or the Wikimedia Foundation. It is not medical or legal advice — cannabis law varies by jurisdiction and changes often.
