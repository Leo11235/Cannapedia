# Getting your brother editing Cannapedia (free, iPad-friendly)

This walks through turning on the web editor that's built into the project, plus the extra tools added alongside it: a preview-before-publish safety step, a Markdown file importer, automatic content checks, and visit analytics. Once this is done, your brother logs into a plain website, no terminal, no GitHub account, no app install beyond Safari.

## How it works, in one paragraph

The public Cannapedia site and the editor both live at the same web address, deployed for free by Netlify straight from this GitHub repo. Your brother logs into `/admin` with just an email and password, and has full content control: creating, editing, and deleting articles, categories, and widgets. Saving creates a Draft, not a live page; he moves it to "Ready" and publishes it himself when he's happy with the preview, no approval from you required, it's just a self-check step before anything goes live. Your job going forward is the code side (new features, layout, new widget types), not day-to-day content.

## One-time setup (you do this, from a regular computer)

**1. Push these changes.** From your normal git workflow (VS Code, GitHub Desktop, or terminal):
```
git add -A
git commit -m "Add editor, import tool, validation, and analytics"
git push
```

**2. Create a free Netlify account** at netlify.com, signing in with your GitHub account (simplest, avoids a separate password).

**3. Add the site.** Click "Add new site" → "Import an existing project" → GitHub → authorize Netlify → select the `Cannapedia` repo. Netlify will read `netlify.toml` automatically and already know the build command and output folder. Click Deploy.

**4. Set the site name.** In Site configuration → General → Site details, change the site name to something like `cannapedia` so your URL is `cannapedia.netlify.app`. (If that exact name is taken, pick another, then open `admin/config.yml` in the repo and update the `site_url:` line to match, commit, and push again.)

**5. Turn on Identity.** Site configuration → Identity → Enable Identity.
   - Under Registration, set it to **Invite only**. This is the important security setting: it means no stranger can ever create their own account, only people you personally invite.

**6. Turn on Git Gateway.** Still under Identity → Services, click Enable Git Gateway. This is what lets saves turn into real commits without anyone touching GitHub directly.

**7. Create the `drafts` branch.** This is only needed for the Markdown importer (see below). From your normal git tool: `git checkout -b drafts && git push -u origin drafts`. Netlify automatically builds a preview for any branch by default, so this alone gives you a working preview URL at `drafts--<your-site-name>.netlify.app`.

**8. Invite your brother.** Identity tab → Invite users → enter his email. He'll get an email invite. It's worth inviting yourself too, so you have the same editor available.

**9. Sign up for analytics (optional but free).** Go to goatcounter.com, create a free account, and it'll give you a code/subdomain like `yourname.goatcounter.com`. Open `templates/base.html`, find the line with `CODE.goatcounter.com`, and replace `CODE` with yours. Commit and push. GoatCounter doesn't use cookies and doesn't collect personal data, so it needs no cookie-consent banner.

That's the whole setup. Total cost: $0 (a custom domain later would be the only optional paid step, roughly $10-15/year).

## What your brother does, on his iPad

1. Open Safari, click the invite link in his email, set a password.
2. Go to `https://cannapedia.netlify.app/admin`, log in.
3. Optional but nice: tap Share → "Add to Home Screen" so it sits on his iPad like an app.
4. From there it's mostly forms: New Article, or click an existing one to edit or delete. Title, short description, categories (one per line, these double as tags), status, an optional infobox, optional sidebar widgets (trivia, quote, timeline, related articles), and the main article text box. He can drop photos in directly from his Camera Roll using the image buttons.
5. Hit Save. This creates a Draft, not a live page yet.
6. Open the **Workflow** view (left sidebar in the editor). His draft is there with a live preview. When it looks right, move it to Ready, then click **Publish**. That's the moment it actually goes live, and he can do all of this himself.
7. A small "Editor v1.0 · What's new" button sits in the bottom-right corner of the editor at all times, showing what's changed in the tool itself since the last update.

## The Markdown importer (for pasting/uploading a whole .md file)

At `/admin/import.html` there's a second, simpler tool: paste or upload a complete Markdown file (frontmatter and all, the same shape as any file in `content/articles/`) and it commits straight to the `drafts` branch. It does not touch the live site. After committing, it gives you two links: a preview URL to check the rendered article, and a GitHub link to open (and merge) a pull request, merging that pull request is what actually publishes it. Because the merge step happens on GitHub itself, this half of the workflow needs a GitHub account, practically this tool is for you (or anyone with repo access), not your brother, who only has a Netlify Identity login. He should keep using the regular form-based editor described above.

## Automatic content checks

Every build (both the live site and every preview) now runs a validation pass before writing anything out. Real problems, like a "related articles" widget pointing to an article that doesn't exist, a duplicate URL, or a malformed widget, fail the build outright and leave the previous version untouched, so a bad save can't quietly break a page. Smaller issues, like a missing short description, print as warnings in the build log but don't block anything. You can see this log in Netlify's dashboard under Deploys.

## Notes on safety, honestly stated

Nothing on the internet is unhackable, but this setup is about as low-risk as a small site gets. The public Cannapedia pages are plain static HTML, there's no database and no server code for anyone to attack. The only login anywhere is Netlify's own Identity system (not something custom-built), and it's invite-only, so no public sign-up form exists at all; the two of you are the only accounts that can ever exist. Publishing is a deliberate second step (Draft → Ready → Publish) rather than instant, which catches typos and mistakes before they're live, without requiring anyone else's approval.

On the code side: since both of you now push to the same repo (your brother indirectly, through the editor; you directly, with code changes), always `git pull` before you start editing and again right before you push, and never `git push --force` to `main`. It's also worth turning on GitHub's branch protection for `main` (Settings → Branches → add a rule → "Restrict force pushes") -- a one-time checkbox that rules out the one command that could actually discard someone else's commits, without slowing down anyone's normal saves or publishes.

## If something needs to change later

- To add a new sidebar widget type, or change what fields show up in the editor, edit `admin/config.yml`.
- To bump the editor's version number and changelog, edit `admin/changelog.json`.
- To change what categories/tags look like or how the site renders, the actual page templates are in `templates/`, unchanged by any of this.
- Your brother never needs to know any of this exists beyond the login form and the "What's new" button.
