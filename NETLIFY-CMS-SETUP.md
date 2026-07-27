# Getting your brother editing Cannapedia (free, iPad-friendly)

This walks through turning on the web editor that's now built into the project. Once this is done, your brother logs into a plain website, no terminal, no GitHub account, no app install beyond Safari.

## How it works, in one paragraph

The public Cannapedia site and the editor both live at the same web address, deployed for free by Netlify straight from this GitHub repo. Your brother logs into `/admin` with just an email and password. When he saves an article, it becomes a draft, not a live page. You review it (there's a live preview) and click Publish when it's ready, which is what actually makes it appear on the real site. Nothing he does can break or vandalize the live encyclopedia without your sign-off.

## One-time setup (you do this, from a regular computer)

**1. Push these changes.** From your normal git workflow (VS Code, GitHub Desktop, or terminal):
```
git add -A
git commit -m "Add editor (Decap CMS) and Netlify deploy config"
git push
```

**2. Create a free Netlify account** at netlify.com, signing in with your GitHub account (simplest, avoids a separate password).

**3. Add the site.** Click "Add new site" → "Import an existing project" → GitHub → authorize Netlify → select the `Cannapedia` repo. Netlify will read `netlify.toml` automatically and already know the build command and output folder. Click Deploy.

**4. Set the site name.** In Site configuration → General → Site details, change the site name to something like `cannapedia` so your URL is `cannapedia.netlify.app`. (If that exact name is taken, pick another, then open `admin/config.yml` in the repo and update the `site_url:` line to match, commit, and push again.)

**5. Turn on Identity.** Site configuration → Identity → Enable Identity.
   - Under Registration, set it to **Invite only**. This is the important security setting: it means no stranger can ever create their own account, only people you personally invite.

**6. Turn on Git Gateway.** Still under Identity → Services, click Enable Git Gateway. This is what lets your brother's saves turn into real commits without him ever touching GitHub.

**7. Invite your brother.** Identity tab → Invite users → enter his email. He'll get an email invite. It's worth inviting yourself too, so you can use the same editor to review and publish his drafts.

That's the whole setup. Total cost: $0. Netlify's free tier is far more bandwidth and build time than a personal wiki like this will ever use.

## What your brother does, on his iPad

1. Open Safari, click the invite link in his email, set a password.
2. Go to `https://cannapedia.netlify.app/admin`, log in.
3. Optional but nice: tap Share → "Add to Home Screen" so it sits on his iPad like an app.
4. From there it's just forms: New Article, or click an existing one to edit. Title, short description, categories (one per line), an optional infobox, optional sidebar cards (trivia, quote, timeline, related articles), and the main article text box. He can drop photos in directly from his Camera Roll using the image buttons.
5. Hit Save. This creates a draft, it is not live yet.

## What you do to publish his work

Open the same `/admin` panel and look for the "Editorial Workflow" board (or the "Workflow" tab). You'll see his draft there with a preview. Read it over, and when you're happy, click Publish (or move it to "Ready" then merge). The live site rebuilds automatically, usually inside a minute.

## Notes on safety, honestly stated

Nothing on the internet is unhackable, but this setup is about as low-risk as a small site gets. The public Cannapedia pages are plain static HTML, there's no database and no server code for anyone to attack. The only login anywhere is Netlify's own Identity system (not something custom-built), it's invite-only so no public sign-up exists, and even a compromised account can only create a draft, since publishing is a separate manual step you control. If you ever want to tighten it further, you can require two-factor login on your own Netlify account, and keep the GitHub repo private (it can be either; being private just hides the source files from search engines, it doesn't change how the editor works).

## If something needs to change later

- To add a new sidebar widget type, or change what fields show up in the editor, edit `admin/config.yml`.
- To change what categories/tags look like or how the site renders, the actual page templates are in `templates/`, unchanged by any of this.
- Your brother never needs to know any of this exists; it's all invisible to him behind the login form.
