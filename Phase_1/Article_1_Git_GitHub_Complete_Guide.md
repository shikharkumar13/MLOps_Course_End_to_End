# Article 1: Git & GitHub — The Complete Guide for ML Practitioners

---

## 📋 Learning Roadmap

Before diving in, here is the full sequence of topics covered across both articles:

| # | Topic | Article |
|---|-------|---------|
| 1 | Why Git? The problem it solves | 1 |
| 2 | Core Concepts: Repos, Staging, Commits, Branches | 1 |
| 3 | Installation & First-time Setup | 1 |
| 4 | Essential Daily Commands | 1 |
| 5 | Branching & Merging | 1 |
| 6 | Undoing Mistakes | 1 |
| 7 | Working with GitHub (Remote Repos) | 1 |
| 8 | .gitignore for ML Projects | 1 |
| 9 | Collaboration Workflows | 1 |
| 10 | Hands-on: Iris Classification Project with Git | 2 |
| 11 | Simulating Real-world Scenarios (bugs, rollbacks, PRs) | 2 |

---

## Part 1 — Why Git? The Problem It Solves

### The Nightmare Without Version Control

Imagine you are building a machine learning model to predict customer churn. Over the course of two weeks, your project folder looks like this:

```
churn_model/
├── model.py
├── model_v2.py
├── model_v2_final.py
├── model_v2_final_ACTUALLY_FINAL.py
├── model_backup_before_i_broke_it.py
├── model_johns_changes.py
├── model_johns_changes_merged_with_mine.py
```

This is not hypothetical — this is what every developer and data scientist does before learning Git. Now consider what happens when:

- **You break something** that was working yesterday and cannot remember what you changed.
- **Your teammate edits the same file** as you and you both overwrite each other's work.
- **Your manager asks**: "Can you roll back to the version from last Tuesday that the client approved?"
- **You want to try a new feature** (say, a different algorithm) without breaking your working code.
- **You want to show your work publicly** so recruiters or collaborators can see it.

Every one of these scenarios is painful without version control. Git solves all of them cleanly.

---

### What Exactly Does Git Do?

Git is a **distributed version control system**. Let's unpack that:

**Version Control** means Git tracks every change you make to your files over time — who changed what, when, and why. Think of it like "Google Docs version history" but for entire codebases, with surgical precision.

**Distributed** means every developer has the **complete history** of the project on their own machine. There is no single point of failure. Even if the server goes down, your full history is local.

Here is what Git gives you concretely:

| Problem | Git's Solution |
|---------|---------------|
| "I broke something, how do I go back?" | Revert to any previous commit |
| "I want to try something risky" | Create a branch; merge only when it works |
| "My teammate overwrote my code" | Merge system handles conflicts explicitly |
| "What changed since yesterday?" | `git diff`, `git log` show exact changes |
| "Can we release v1 while working on v2?" | Branches for stable vs development versions |
| "I need to share my code with the world" | Push to GitHub (remote repository) |

---

### Git vs GitHub — They Are NOT the Same Thing

This is the most common point of confusion for beginners.

- **Git** is a tool that runs on your computer. It tracks changes locally.
- **GitHub** is a website (github.com) that hosts your Git repositories in the cloud.

The analogy: Git is like Microsoft Word's "Track Changes" feature. GitHub is like Google Drive — a place to store and share your documents.

You can use Git without GitHub (purely locally). You cannot meaningfully use GitHub without Git. In ML, you use both: Git locally to track experiments, GitHub to collaborate, deploy, and showcase your work.

---

## Part 2 — Core Concepts You Must Understand

These four concepts underpin everything in Git. Do not rush past them.

### 1. Repository (Repo)

A **repository** is a directory (folder) that Git is tracking. It contains all your project files plus a hidden `.git` folder where Git stores its entire history. When you run `git init` in a folder, that folder becomes a repository.

```
my_ml_project/       ← This is your repository
├── .git/            ← Hidden folder; Git's brain. Never touch this manually
├── train.py
├── model.py
└── requirements.txt
```

### 2. The Three Zones

This is the most important concept in Git. Every file you work with exists in one of three zones:

```
┌─────────────────┐     git add      ┌──────────────────┐    git commit    ┌──────────────────┐
│  Working        │ ───────────────► │  Staging Area    │ ───────────────► │  Local           │
│  Directory      │                  │  (Index)         │                  │  Repository      │
│                 │ ◄─────────────── │                  │                  │                  │
│  (Your files    │   git restore    │  (Changes you    │                  │  (Permanent      │
│   on disk)      │                  │   want to save)  │                  │   history)       │
└─────────────────┘                  └──────────────────┘                  └──────────────────┘
                                                                                    │
                                                                                    │ git push
                                                                                    ▼
                                                                           ┌──────────────────┐
                                                                           │  Remote Repo     │
                                                                           │  (GitHub)        │
                                                                           └──────────────────┘
```

- **Working Directory**: Where you edit your files normally. Git knows these files exist but may or may not be tracking changes.
- **Staging Area**: A waiting room. You selectively add changes here before committing. This lets you commit only part of your work.
- **Local Repository**: The permanent history. Once committed, it is saved forever (unless you explicitly remove it).
- **Remote Repository**: The cloud copy on GitHub.

### 3. Commit

A **commit** is a snapshot of your staged changes saved to the repository, along with a message describing what you did. Think of commits as save points in a video game — you can always return to any of them.

Each commit has:
- A unique ID (called a **SHA hash**) like `a3f5c2d`
- The author's name and email
- A timestamp
- A message you wrote
- A pointer to the previous commit (forming a chain)

### 4. Branch

A **branch** is an independent line of development. The default branch is called `main` (or `master` in older repos). When you create a new branch, you get a copy of the current state to experiment on — without touching the original.

```
main branch:    A ── B ── C ──────────────── F (merged)
                               \            /
feature branch:                 D ── E ────
```

In ML, you might use branches like:
- `main` — stable, production-ready code
- `feature/add-random-forest` — experimenting with a new model
- `fix/memory-leak` — fixing a bug

---

## Part 3 — Installation & First-Time Setup

### Installing Git

**macOS:**
```bash
brew install git
# or just type 'git' in terminal — macOS will prompt you to install Xcode tools
```

**Ubuntu/Debian Linux:**
```bash
sudo apt update
sudo apt install git
```

**Windows:**
Download from https://git-scm.com/download/win and use the installer. This also installs Git Bash (a terminal for running Git commands on Windows).

**Verify installation:**
```bash
git --version
# Output: git version 2.43.0
```

---

### First-Time Configuration

Git needs to know who you are before you make any commit. Run these once on any new machine:

```bash
# Set your name (appears in every commit you make)
git config --global user.name "Your Name"

# Set your email (use the same email as your GitHub account)
git config --global user.email "you@example.com"

# Set the default branch name to 'main' (modern standard)
git config --global init.defaultBranch main

# Set VS Code as your default editor (optional but recommended)
git config --global core.editor "code --wait"
```

**What does `--global` mean?** It applies this setting to ALL your Git repos on this computer. You can also set config per-project by omitting `--global` (inside that project's folder).

**View all your settings:**
```bash
git config --list
```

---

### Connecting to GitHub with SSH (One-time Setup)

HTTPS asks for your password every push. SSH is more secure and password-free after setup.

```bash
# Step 1: Generate an SSH key pair
ssh-keygen -t ed25519 -C "you@example.com"
# Press Enter 3 times to accept defaults

# Step 2: Copy your PUBLIC key
cat ~/.ssh/id_ed25519.pub
# Copy the entire output

# Step 3: Go to GitHub → Settings → SSH Keys → New SSH Key
# Paste what you copied and save

# Step 4: Test the connection
ssh -T git@github.com
# Output: Hi username! You've successfully authenticated.
```

---

## Part 4 — Essential Daily Commands

This section covers every command you will use day-to-day. Each command includes what it does, when to use it, and real examples.

---

### `git init` — Start Tracking a Project

**What it does:** Turns any folder into a Git repository by creating a hidden `.git` folder inside it.

**When to use:** At the very beginning of any new project.

```bash
mkdir iris_classifier
cd iris_classifier
git init
# Output: Initialized empty Git repository in /iris_classifier/.git/
```

> ⚠️ Never run `git init` inside an existing Git repo (like your home folder). This creates "nested repos" which cause confusion.

---

### `git clone` — Download an Existing Repository

**What it does:** Downloads a complete copy of a remote repository (from GitHub) to your local machine, including all history, branches, and commits.

**When to use:** When you want to work on an existing project from GitHub.

```bash
# Clone using HTTPS
git clone https://github.com/username/iris_classifier.git

# Clone using SSH (preferred after SSH setup)
git clone git@github.com:username/iris_classifier.git

# Clone into a specific folder name
git clone git@github.com:username/iris_classifier.git my_project
```

After cloning, Git automatically sets up the remote called `origin` pointing back to GitHub.

---

### `git status` — See What's Going On

**What it does:** Shows the current state of your working directory and staging area — which files are modified, staged, or untracked.

**When to use:** Constantly. Before and after every operation. This is your GPS.

```bash
git status
```

**Example output explained:**

```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:      ← Modified but not yet staged
  (use "git add <file>..." to update what will be committed)
        modified:   model.py

Untracked files:                    ← New files Git has never seen
  (use "git add <file>..." to include in what will be committed)
        requirements.txt

nothing added to commit but untracked files present
```

**Short form:**
```bash
git status -s
# M  model.py        (M = modified)
# ?? requirements.txt  (?? = untracked)
```

---

### `git add` — Stage Changes

**What it does:** Moves changes from the Working Directory to the Staging Area, preparing them for the next commit.

**When to use:** After editing files, before committing. You decide exactly what goes into each commit.

```bash
# Stage a single file
git add model.py

# Stage multiple specific files
git add model.py train.py

# Stage ALL changes in the current directory (use carefully)
git add .

# Stage all .py files
git add *.py

# Stage parts of a file interactively (advanced — lets you commit half a file)
git add -p model.py
```

> **ML Tip:** Never use `git add .` blindly in ML projects. You might accidentally stage large data files or trained model weights. Always check `git status` first or configure `.gitignore`.

---

### `git commit` — Save a Snapshot

**What it does:** Creates a permanent snapshot of everything in the Staging Area and saves it to the Local Repository with a message.

**When to use:** After staging the changes you want. Commit often — small, focused commits are much better than giant ones.

```bash
# Standard commit with a message inline
git commit -m "Add logistic regression baseline model"

# Stage all modified tracked files AND commit in one step
# (skips staging for files Git already knows about)
git commit -am "Fix accuracy calculation bug"

# Open your editor to write a longer, detailed commit message
git commit
```

**Writing Good Commit Messages** — this matters more than most beginners think:

```bash
# ❌ Bad commit messages
git commit -m "fix"
git commit -m "changes"
git commit -m "asdfgh"

# ✅ Good commit messages (present tense, imperative mood)
git commit -m "Add random forest classifier with 5-fold cross-validation"
git commit -m "Fix data leakage in train-test split"
git commit -m "Remove hardcoded file paths, use config instead"
```

A good commit message completes the sentence: *"If applied, this commit will ___________"*

---

### `git log` — View Commit History

**What it does:** Shows the history of commits on the current branch.

**When to use:** To understand what has been done, find a specific commit, or trace when a bug was introduced.

```bash
# Full log (verbose)
git log

# Compact, one line per commit (most useful)
git log --oneline

# Show last 5 commits
git log --oneline -5

# Show a visual graph of all branches
git log --oneline --graph --all

# Show what files changed in each commit
git log --stat

# Search commits by message keyword
git log --grep="accuracy"

# Show commits by a specific author
git log --author="Jane"
```

**Example `git log --oneline --graph --all` output:**

```
* a3f5c2d (HEAD -> main) Add evaluation metrics
* b1e2d4f Fix preprocessing bug
| * c9d3a11 (feature/random-forest) Add random forest model
|/
* 8a7b3e2 Initial project structure
```

This shows the branching and merging history visually.

---

### `git diff` — See Exactly What Changed

**What it does:** Shows the line-by-line differences between versions of files.

**When to use:** Before staging or committing, to review exactly what you changed.

```bash
# Diff between working directory and last commit (unstaged changes)
git diff

# Diff between staging area and last commit (staged changes)
git diff --staged
# (also written as: git diff --cached)

# Diff between two commits
git diff a3f5c2d b1e2d4f

# Diff between two branches
git diff main feature/random-forest

# Diff for a specific file only
git diff model.py
```

**Reading diff output:**

```diff
- accuracy = correct / total        ← Red lines: what was removed
+ accuracy = correct / len(y_test)  ← Green lines: what was added
```

---

### `git push` — Upload to GitHub

**What it does:** Sends your local commits to the remote repository on GitHub.

**When to use:** After committing locally, to share your work or back it up.

```bash
# Push current branch to its remote counterpart
git push

# First time pushing a new branch
git push -u origin feature/random-forest
# -u sets the upstream: future 'git push' on this branch needs no arguments

# Push to a specific remote and branch
git push origin main

# Force push (DANGEROUS — rewrites remote history, never on shared branches)
git push --force
```

> ⚠️ `git push --force` on a shared branch like `main` can destroy your teammates' work. Only use it on your own private branches.

---

### `git pull` — Download Changes from GitHub

**What it does:** Fetches new commits from the remote repository AND merges them into your current local branch. It is essentially `git fetch` + `git merge` in one command.

**When to use:** Before starting work each day, or whenever someone tells you they pushed new code.

```bash
# Pull changes for the current branch
git pull

# Pull from a specific remote and branch
git pull origin main

# Pull using rebase instead of merge (cleaner history, for advanced users)
git pull --rebase origin main
```

---

### `git fetch` — Download Without Merging

**What it does:** Downloads new commits and branches from remote but does NOT change your local working files. It is a safe way to "peek" at what's on the remote.

**When to use:** When you want to see what others have pushed without immediately merging it.

```bash
# Fetch all changes from remote
git fetch origin

# After fetching, compare with your local branch
git diff main origin/main

# Then merge when you're ready
git merge origin/main
```

> **`git pull` vs `git fetch`**: `pull` is automatic (fetch + merge). `fetch` lets you inspect before merging. For beginners, `pull` is fine. On teams, `fetch` gives you more control.

---

## Part 5 — Branching & Merging

Branching is where Git's power truly shows. This is crucial for ML projects where you experiment with different models, hyperparameters, or preprocessing approaches simultaneously.

### Creating and Switching Branches

```bash
# List all local branches (* marks the current one)
git branch

# List all branches including remote ones
git branch -a

# Create a new branch (does NOT switch to it)
git branch feature/add-svm-model

# Switch to an existing branch
git switch feature/add-svm-model
# (older syntax: git checkout feature/add-svm-model)

# Create a new branch AND switch to it immediately (most common workflow)
git switch -c feature/add-svm-model
# (older syntax: git checkout -b feature/add-svm-model)

# Delete a branch (only after merging)
git branch -d feature/add-svm-model

# Force delete an unmerged branch (permanent — use with care)
git branch -D feature/add-svm-model
```

---

### Merging Branches

**What it does:** Integrates the changes from one branch into another.

```bash
# Step 1: Switch to the branch you want to merge INTO
git switch main

# Step 2: Merge the feature branch into it
git merge feature/add-svm-model
```

**Fast-forward merge** (clean, no merge commit created):

```
Before:   main: A ── B
                       \
          feature:      C ── D

After:    main: A ── B ── C ── D   (feature just "caught up")
```

**Three-way merge** (creates a merge commit, happens when both branches have new commits):

```
Before:   main:    A ── B ── E
                        \
          feature:        C ── D

After:    main:    A ── B ── E ── M   (M is the merge commit)
                        \         /
          feature:        C ── D
```

---

### Merge Conflicts — Don't Panic

A **merge conflict** happens when two branches changed the **same line** of the same file differently. Git cannot decide which version to keep, so it asks you.

```bash
git merge feature/new-preprocessing
# Output:
# CONFLICT (content): Merge conflict in preprocess.py
# Automatic merge failed; fix conflicts and then commit the result.
```

Open `preprocess.py` and you will see conflict markers:

```python
<<<<<<< HEAD                         ← Your current branch (main)
scaler = StandardScaler()
=======                              ← Divider
scaler = MinMaxScaler()
>>>>>>> feature/new-preprocessing    ← The incoming branch
```

**To resolve:**
1. Edit the file to keep the correct code (delete the markers)
2. `git add preprocess.py`
3. `git commit` (Git auto-generates a merge commit message)

---

### `git rebase` — An Alternative to Merge

**What it does:** Replays your branch's commits on top of another branch, giving a linear (cleaner) history. Instead of a merge commit, it looks like you branched off the latest code.

```bash
# While on feature branch:
git rebase main
```

```
Before rebase:   main:    A ── B ── E
                               \
                 feature:       C ── D

After rebase:    main:    A ── B ── E
                                     \
                 feature:             C' ── D'  (commits replayed on top of E)
```

> **Rule of thumb**: Rebase your own feature branches to keep history clean. Never rebase shared branches like `main` — it rewrites history and breaks other people's work.

---

## Part 6 — Undoing Mistakes

Every developer makes mistakes. Git is designed to let you undo almost anything safely.

### `git restore` — Undo Unstaged Changes

**What it does:** Discards changes in the working directory, reverting a file to its last committed state.

```bash
# Discard changes in a specific file (PERMANENT — use carefully)
git restore model.py

# Discard all unstaged changes
git restore .

# Unstage a file (move it out of staging area back to working directory)
git restore --staged model.py
```

> ⚠️ `git restore` on the working directory is **permanent**. Your unsaved edits are gone. Only do this when you are sure.

---

### `git reset` — Move the Branch Pointer Back

**What it does:** Moves the current branch's tip to a previous commit. Has three modes:

```bash
# --soft: Uncommit but keep changes staged
# (commit is undone, but files are in staging area)
git reset --soft HEAD~1

# --mixed (default): Uncommit and unstage, but keep changes in working dir
git reset HEAD~1
git reset --mixed HEAD~1

# --hard: Uncommit, unstage, AND discard all changes (DANGEROUS)
git reset --hard HEAD~1

# Reset to a specific commit SHA
git reset --hard a3f5c2d
```

**What is `HEAD~1`?** HEAD is the current commit. `~1` means "one commit before HEAD." `~3` means three commits back.

| Mode | Commit undone? | Staging cleared? | Working dir changed? |
|------|---------------|-----------------|---------------------|
| `--soft` | ✅ | ❌ | ❌ |
| `--mixed` | ✅ | ✅ | ❌ |
| `--hard` | ✅ | ✅ | ✅ |

---

### `git revert` — Safely Undo a Commit

**What it does:** Creates a new commit that undoes the changes of a specific commit. Unlike `reset`, it does not rewrite history — it is safe to use on shared branches.

```bash
# Revert the last commit
git revert HEAD

# Revert a specific commit
git revert a3f5c2d

# Revert without opening the editor (auto-generates the message)
git revert HEAD --no-edit
```

> **`reset` vs `revert`**: Use `reset` only on commits that exist locally and haven't been pushed. Use `revert` when the commit is already on GitHub and shared with others.

---

### `git stash` — Temporarily Set Aside Work

**What it does:** Saves your uncommitted changes on a temporary stack and cleans your working directory, so you can switch context without committing half-done work.

```bash
# Stash current changes (with a descriptive message)
git stash push -m "WIP: experimenting with gradient boosting"

# List all stashes
git stash list
# Output:
# stash@{0}: On main: WIP: experimenting with gradient boosting
# stash@{1}: On main: trying new feature engineering

# Apply the most recent stash (and keep it in the stash list)
git stash apply

# Apply AND remove from stash list
git stash pop

# Apply a specific stash
git stash apply stash@{1}

# Delete a stash
git stash drop stash@{0}

# Delete all stashes
git stash clear
```

**Real ML scenario:** You are in the middle of rewriting your feature engineering code when your manager says "there's a production bug — fix it now." You stash your half-done work, switch to `main`, fix the bug, commit and push, then come back and `git stash pop` your work.

---

### `git cherry-pick` — Copy a Specific Commit

**What it does:** Applies the changes of a specific commit from any branch onto your current branch.

```bash
# Apply commit a3f5c2d onto the current branch
git cherry-pick a3f5c2d
```

**Real ML scenario:** You fixed a data normalization bug on a feature branch. Without merging the whole feature branch, you can cherry-pick just that fix onto `main`.

---

## Part 7 — Working with GitHub (Remote Repositories)

### Creating a New GitHub Repository

1. Go to github.com → click **"New repository"**
2. Name it (e.g., `iris-classifier`)
3. Set to Public or Private
4. Do NOT initialize with README if you already have local code
5. Click **Create repository**

Then connect your local repo:

```bash
# Add GitHub as the remote (named 'origin')
git remote add origin git@github.com:username/iris-classifier.git

# Verify
git remote -v
# origin  git@github.com:username/iris-classifier.git (fetch)
# origin  git@github.com:username/iris-classifier.git (push)

# Push local code to GitHub for the first time
git push -u origin main
```

---

### Forking a Repository

A **fork** is your personal copy of someone else's repository on GitHub. It lives under your account and you have full control. This is how open-source collaboration works.

1. On GitHub, navigate to the repo you want to contribute to
2. Click the **Fork** button (top right)
3. Clone your fork locally:
   ```bash
   git clone git@github.com:YOUR_USERNAME/original-repo.git
   ```
4. Add the original as an "upstream" remote to pull future updates:
   ```bash
   git remote add upstream git@github.com:ORIGINAL_OWNER/original-repo.git
   ```
5. Sync your fork with the original:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

---

### Pull Requests (PRs)

A **Pull Request** is a proposal to merge your branch/fork into another branch. This is the standard way to contribute code in teams and open source.

**Workflow:**

```bash
# 1. Create a feature branch
git switch -c feature/add-xgboost-model

# 2. Make your changes and commit
git add .
git commit -m "Add XGBoost model with GridSearchCV tuning"

# 3. Push the branch to GitHub
git push -u origin feature/add-xgboost-model
```

4. On GitHub, you'll see a prompt: **"Compare & pull request"** — click it.
5. Write a clear title and description.
6. Request reviewers if working on a team.
7. After approval → **Merge pull request**.

---

### Tags — Marking Releases

Tags mark specific commits as important milestones (e.g., v1.0, v2.0-beta).

```bash
# Create a lightweight tag
git tag v1.0

# Create an annotated tag (preferred — includes message)
git tag -a v1.0 -m "First stable model release, 92% accuracy on test set"

# List all tags
git tag

# Push tags to GitHub (not pushed by default)
git push origin v1.0

# Push all tags
git push --tags

# View tag details
git show v1.0
```

---

## Part 8 — .gitignore for ML Projects

A `.gitignore` file tells Git which files to **never track**. This is essential for ML projects.

**Why it matters in ML:**
- Data files can be gigabytes (Git is not a data storage system)
- Trained models can be hundreds of MBs
- API keys/credentials must never be committed
- Temporary files clutter your history

Create a file named `.gitignore` in your project root:

```gitignore
# ─────────────────────────────────────────
# Python
# ─────────────────────────────────────────
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# ─────────────────────────────────────────
# Jupyter Notebooks
# ─────────────────────────────────────────
.ipynb_checkpoints/
*.ipynb_checkpoints

# ─────────────────────────────────────────
# Data Files (track with DVC or store in S3 instead)
# ─────────────────────────────────────────
data/raw/
data/processed/
*.csv
*.tsv
*.json
*.parquet
*.feather
*.h5
*.hdf5
*.pkl
*.pickle
*.npy
*.npz

# ─────────────────────────────────────────
# Trained Models (can be large)
# ─────────────────────────────────────────
models/
*.pt         # PyTorch
*.pth        # PyTorch
*.onnx
*.pb         # TensorFlow
*.h5         # Keras
*.joblib
*.model

# ─────────────────────────────────────────
# Secrets & Config (NEVER commit these)
# ─────────────────────────────────────────
.env
.env.local
config/secrets.yaml
*.key
*.pem

# ─────────────────────────────────────────
# IDE & OS
# ─────────────────────────────────────────
.vscode/
.idea/
*.DS_Store
Thumbs.db

# ─────────────────────────────────────────
# MLflow / Experiment Tracking
# ─────────────────────────────────────────
mlruns/
mlflow.db

# ─────────────────────────────────────────
# Logs & Outputs
# ─────────────────────────────────────────
logs/
*.log
outputs/
```

> **What DO you commit in ML?** Code (`.py`), configuration files (`.yaml`/`.json` without secrets), `requirements.txt`, `README.md`, small sample data for testing, and notebooks (`.ipynb`) — though it's debated for large notebooks.

---

## Part 9 — Collaboration Workflows

### The Feature Branch Workflow (Standard for Teams)

This is the most common workflow for ML teams:

```
main  ←── always stable, deployable code
 │
 ├── feature/data-augmentation     ← each feature is a branch
 ├── feature/hyperparameter-tuning
 ├── fix/fix-class-imbalance
 └── experiment/vision-transformer
```

**Day-to-day workflow:**

```bash
# 1. Always start by pulling latest main
git switch main
git pull origin main

# 2. Create a feature branch
git switch -c feature/add-bert-embeddings

# 3. Work on your feature (multiple commits)
git add embeddings.py
git commit -m "Add BERT tokenizer integration"

git add train.py
git commit -m "Update training loop for embedding inputs"

# 4. Keep your branch updated with main as others merge code
git fetch origin
git rebase origin/main

# 5. Push and open a Pull Request
git push -u origin feature/add-bert-embeddings
# Then open PR on GitHub
```

---

### Useful Commands Summary Table

| Command | What it does |
|---------|-------------|
| `git init` | Initialize a new repository |
| `git clone <url>` | Download a remote repository |
| `git status` | Show current state of working dir & staging area |
| `git add <file>` | Stage a file for commit |
| `git add .` | Stage all changes |
| `git commit -m "msg"` | Commit staged changes |
| `git log --oneline` | View compact commit history |
| `git diff` | Show unstaged changes |
| `git diff --staged` | Show staged changes |
| `git push` | Upload commits to GitHub |
| `git pull` | Download & merge remote changes |
| `git fetch` | Download remote changes (no merge) |
| `git branch` | List branches |
| `git switch -c <name>` | Create & switch to new branch |
| `git switch <name>` | Switch to existing branch |
| `git merge <branch>` | Merge a branch into current |
| `git rebase <branch>` | Rebase onto another branch |
| `git restore <file>` | Discard working directory changes |
| `git restore --staged <file>` | Unstage a file |
| `git reset --soft HEAD~1` | Undo last commit, keep staged |
| `git reset --hard HEAD~1` | Undo last commit, discard changes |
| `git revert HEAD` | Safely undo last commit (new commit) |
| `git stash` | Save unfinished work temporarily |
| `git stash pop` | Restore stashed work |
| `git cherry-pick <sha>` | Copy a specific commit to current branch |
| `git tag -a v1.0 -m "msg"` | Create an annotated tag |
| `git remote add origin <url>` | Link local repo to GitHub |
| `git remote -v` | View remote URLs |

---

## Summary

You have now learned:

✅ **Why Git exists** and what specific problems it solves for ML practitioners  
✅ **The three zones** (Working Directory → Staging → Repository) — the heart of Git  
✅ **All essential commands** with real ML-flavored examples  
✅ **Branching and merging** for parallel experimentation  
✅ **Undoing mistakes** safely with restore, reset, revert, and stash  
✅ **GitHub workflows** — remotes, PRs, forks, and tags  
✅ **A proper `.gitignore`** for ML projects  
✅ **Team collaboration patterns** using the feature branch workflow  

Head to **Article 2** to put all of this into practice on a real ML classification project, running through every command in context.
