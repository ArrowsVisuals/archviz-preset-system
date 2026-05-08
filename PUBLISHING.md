# Publishing Guide — ArchViz Preset System

This is your step-by-step guide to publishing this package as **ArrowsVisuals/archviz-preset-system** on GitHub and ComfyUI Manager.

Read through once before starting. Total time is about 15-20 minutes if you don't hit any snags.

---

## What you need before starting

- A GitHub account at **github.com/ArrowsVisuals** (create it now if it doesn't exist)
- Git installed locally — verify with `git --version` in your terminal
- The unzipped `archviz-preset-system` folder somewhere on your machine
- About 20 minutes

---

## Step 1: Create the GitHub repository

1. Go to **https://github.com/new** while signed in as ArrowsVisuals
2. Fill in:
   - **Repository name:** `archviz-preset-system`
   - **Description:** `ComfyUI custom node package for high-end architectural visualization prompt construction with Nano Banana Pro / Gemini 3 Pro Image`
   - **Visibility:** Public *(required for ComfyUI Manager submission)*
   - **Do NOT** check "Add a README", "Add .gitignore", or "Choose a license" — we already have all three
3. Click **Create repository**

GitHub will show you a "quick setup" page with terminal commands. Keep this tab open — you'll reference it in step 2.

---

## Step 2: Push the code to GitHub

Open a terminal and navigate to wherever you unzipped the folder:

```bash
cd path/to/archviz-preset-system
```

Then run these commands one at a time:

```bash
# Initialize git in this folder (use 'main' as default branch name)
git init -b main

# Stage every file
git add .

# Make the first commit
git commit -m "Initial release v3.0.0"

# Connect to your new GitHub repo
git remote add origin https://github.com/ArrowsVisuals/archviz-preset-system.git

# Push to GitHub
git push -u origin main
```

### Authentication

When `git push` asks for credentials:

- **Username:** `ArrowsVisuals`
- **Password:** *use a Personal Access Token, not your GitHub password*

To create a Personal Access Token:

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Note: `ComfyUI publishing`
4. Expiration: 90 days (or longer if you prefer)
5. Scopes: check **`repo`** (full control of private repositories — needed even for public ones)
6. Click **Generate token** at the bottom
7. **Copy the token now** — GitHub only shows it once
8. Paste it as the password when git prompts

After a successful push, refresh your repo page on GitHub. All 18 files should be visible.

---

## Step 3: Verify the GitHub Action runs

The repo includes `.github/workflows/validate.yml` which auto-runs on every push. Within a minute of pushing:

1. Go to your repo's **Actions** tab
2. You should see "Validate" workflow listed with a green checkmark
3. If it's red, click in to see what failed

A green checkmark means the JSON is valid and the Python compiles — proof the package is healthy.

---

## Step 4: Create the v3.0.0 release

A "release" gives users a stable downloadable zip separate from the live code on `main`.

1. On your repo page, click **Releases** in the right sidebar (or visit `https://github.com/ArrowsVisuals/archviz-preset-system/releases`)
2. Click **Create a new release**
3. Click **Choose a tag** → type `v3.0.0` → click **Create new tag: v3.0.0 on publish**
4. **Release title:** `v3.0.0 — Initial Release`
5. **Description:** Copy the v3.0.0 section from `CHANGELOG.md` (the "## [3.0.0]" block including all the Added/Changed/Removed bullets)
6. Leave "Set as the latest release" checked
7. Click **Publish release**

GitHub auto-generates a downloadable zip at the release URL. People who can't or don't want to use git can grab that.

---

## Step 5: Test the install yourself

This is the most important step before announcing the package. Test that someone fresh can install it cleanly.

On any machine with ComfyUI:

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/ArrowsVisuals/archviz-preset-system.git
```

Restart ComfyUI fully (kill the process, restart). Watch the console — you should see:

```
[ArchViz] First run — copied default presets to /path/to/ComfyUI/user/archviz_presets.json
[ArchViz] v3 loaded — 3 nodes ((AV) Preset / Matrix / Assembler)
```

Then in ComfyUI:

1. Right-click the canvas → **ArchViz** category should appear with 3 nodes
2. Open `workflows/render_variations_v3.json` from the cloned folder
3. Drop one of your test renders into the input
4. Hit **Queue**
5. Confirm 4 distinct variations appear

If anything fails, fix it and push the fix before announcing. Better to find issues yourself than have users find them.

---

## Step 6: Submit to ComfyUI Manager registry

This makes the package discoverable through ComfyUI Manager's search.

### 6a: Create a publisher account

1. Go to **https://registry.comfy.org/**
2. Click **Sign in** in the top right → use your GitHub account (sign in as ArrowsVisuals)
3. After signing in, click **Create Publisher**
4. Set **Publisher ID:** `arrowsvisuals` *(must be lowercase, 3-30 alphanumeric chars and hyphens)*
5. Set **Display Name:** `Arrows Visuals`
6. Click **Create**

Your `pyproject.toml` already has `PublisherId = "arrowsvisuals"` baked in, so this matches.

### 6b: Generate an API key

1. In the registry dashboard, go to your publisher page
2. Click **API Keys** → **Create API Key**
3. Give it a name like `github-publishing`
4. **Copy the key immediately** — only shown once
5. Save it somewhere safe (1Password, etc.)

### 6c: Add the key to GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `REGISTRY_ACCESS_TOKEN`
4. Value: paste the API key
5. Click **Add secret**

### 6d: Verify the publish workflow is in place

The repo already includes `.github/workflows/publish.yml` — it runs whenever you change `pyproject.toml`. Verify it exists by going to your repo on GitHub → `.github/workflows/` folder → you should see both `publish.yml` and `validate.yml`.

The workflow only runs successfully once the `REGISTRY_ACCESS_TOKEN` secret is set (which you just did in step 6c).

### 6e: Trigger the first publish

The workflow only runs when `pyproject.toml` changes. Trigger it now:

```bash
# Locally:
cd path/to/archviz-preset-system
# Bump version a tiny bit to trigger a publish
sed -i 's/version = "3.0.0"/version = "3.0.1"/' pyproject.toml
git add pyproject.toml
git commit -m "Trigger first registry publish"
git push
```

Or just edit `pyproject.toml` on GitHub directly:
1. Open `pyproject.toml` on your repo
2. Click the pencil icon
3. Change `version = "3.0.0"` to `version = "3.0.1"`
4. Commit changes

Within a minute, check the **Actions** tab. The "Publish to Comfy Registry" workflow should run and complete with green.

After it succeeds, your package appears at:
**`https://registry.comfy.org/nodes/archviz-preset-system`**

It also becomes searchable in ComfyUI Manager:
- ComfyUI Manager → Install Custom Nodes → search "ArchViz" → Install

---

## Step 7: Tell people about it

Once tested and registry-listed, the install instructions are:

**For people with ComfyUI Manager:**
> Search "ArchViz" in ComfyUI Manager → Install Custom Nodes → click Install.

**For people without ComfyUI Manager:**
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/ArrowsVisuals/archviz-preset-system.git
```

**For people who don't use git:**
> Download from https://github.com/ArrowsVisuals/archviz-preset-system/releases — extract the zip into your `ComfyUI/custom_nodes/` folder.

All three need a ComfyUI restart after install.

---

## Updating later

When you change presets or fix bugs:

```bash
# Edit the relevant files (presets/default_presets.json is most common)
git add .
git commit -m "Add 3 new lighting presets"

# Bump version in pyproject.toml (e.g. 3.0.1 → 3.1.0)
# Update CHANGELOG.md with the new version section
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 3.1.0"

# Tag and push
git tag v3.1.0
git push origin main --tags
```

Then on GitHub:
1. Go to Releases → Draft a new release
2. Choose tag `v3.1.0`
3. Title and description from CHANGELOG
4. Publish release

The Comfy Registry auto-detects the new version from `pyproject.toml` and updates the listing.

---

## Troubleshooting

### "git: command not found"
Install git from https://git-scm.com/downloads

### "Authentication failed" or "could not read Username"
You're using your GitHub password instead of a Personal Access Token. Re-read step 2's authentication section.

### "failed to push some refs"
Someone (or you, from a different machine) pushed changes you don't have locally. Run `git pull --rebase origin main` first, then `git push`.

### GitHub Action is red
Click into the failing run on the Actions tab. The error message usually says exactly which JSON or Python file is broken. Most common cause: a typo in `presets/default_presets.json` (extra comma, missing quote).

### Comfy Registry rejects the publish
- Confirm `pyproject.toml` has `PublisherId = "arrowsvisuals"` (matching your registry account)
- Confirm the `REGISTRY_ACCESS_TOKEN` secret exists in GitHub repo settings
- Check the publish.yml action logs for the specific error

### "ArchViz category not appearing in ComfyUI"
The folder is in the wrong place. The structure must be:
```
ComfyUI/custom_nodes/archviz-preset-system/__init__.py
```
Three levels deep. If `__init__.py` ends up directly in `custom_nodes/` you'll break ALL custom nodes.

### Users report the workflow fails to load
The example workflow uses subgraphs (introduced in ComfyUI 0.20). Users on older ComfyUI need to upgrade. The custom nodes themselves work on any version.

---

## A note on iteration

You don't have to get this perfect on the first push. The whole point of versioning is that you can keep improving. Push v3.0.0 today even if you find more presets to add tomorrow — the registry handles updates automatically and users get them via "Update" in ComfyUI Manager.

Better done than perfect.
