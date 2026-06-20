# Article 3: Git + DVC — Versioning Code AND Data for ML Projects

*A hands-on guide to data and model versioning using a Heart Disease classification project*

---

## Introduction

In Articles 1 and 2 you mastered Git for versioning **code**. But there is a problem that Git alone cannot solve well, and it's a problem every ML practitioner hits sooner or later:

> **Git is terrible at handling data and model files.**

This article introduces **DVC (Data Version Control)** — the tool that fills exactly this gap — and shows you how Git and DVC work together as a team. We'll build a complete Heart Disease classification project and version both the code (with Git) and the datasets/models (with DVC).

By the end you will understand:
- Why Git struggles with data and why you need DVC
- How DVC and Git divide the work between them
- The complete DVC workflow: tracking data, remote storage, pipelines, experiments
- How to reproduce any past version of your project — code *and* data *and* model — with a single command

---

## 📋 Learning Roadmap

| # | Topic |
|---|-------|
| 1 | The problem: why Git can't version data |
| 2 | What DVC is and how it works with Git |
| 3 | The mental model: pointers, cache, and remotes |
| 4 | Installation & initializing DVC |
| 5 | Tracking your first dataset |
| 6 | Setting up remote storage |
| 7 | Building a reproducible DVC pipeline |
| 8 | Versioning data + code together |
| 9 | Experiments, metrics, and params |
| 10 | Full Heart Disease project walkthrough |
| 11 | Switching between versions (the payoff) |

---

## Part 1 — The Problem: Why Git Can't Version Data

### Git Was Built for Text, Not Gigabytes

Git was designed to track **source code** — small text files where it stores the line-by-line differences efficiently. When you have a 50 GB dataset or a 2 GB trained neural network, Git falls apart:

| Problem | Consequence |
|---------|------------|
| Git stores full copies of every version of a binary file | Your `.git` folder explodes to hundreds of GBs |
| Git can't compute meaningful diffs on binary files | Every tiny change duplicates the whole file |
| GitHub has a 100 MB per-file hard limit | Your push is rejected outright |
| Cloning becomes painfully slow | New team members wait hours to download history |

### The Naive Workarounds (and Why They Fail)

**"I'll just add data to `.gitignore`"** — Now your data isn't versioned at all. Six months later you can't reproduce the model your client approved, because you don't know which version of the data trained it.

**"I'll store data in a shared drive with folder names like `data_v2_final`"** — You're back to the exact manual-versioning nightmare Git was supposed to solve, but now for data.

**"I'll use Git LFS"** — Better, but limited. It doesn't handle ML pipelines, experiments, metrics tracking, or flexible remote storage (S3, GCS, Azure, SSH) the way DVC does.

### What We Actually Need

We need a system that:
1. Versions large data and model files **without** bloating Git
2. Links a specific data version to a specific code version (so they always match)
3. Stores the actual large files somewhere cheap (cloud storage)
4. Lets you reproduce any past experiment exactly
5. Works **alongside** Git, not against it

That system is **DVC**.

---

## Part 2 — What Is DVC and How Does It Work With Git?

**DVC (Data Version Control)** is an open-source command-line tool that brings Git-like versioning to data and machine learning models. Crucially, it is built to sit **on top of Git**.

### The Key Insight: Git Tracks Pointers, DVC Tracks Data

Here's the elegant trick that makes everything work:

- When you tell DVC to track a large file (say `heart.csv`), DVC moves the actual file into a hidden cache and creates a tiny text file called `heart.csv.dvc`.
- This `.dvc` file is small (a few lines) and contains a **hash (fingerprint)** of your data plus its location.
- **Git tracks the tiny `.dvc` pointer file.** DVC tracks the actual heavy data.

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Project                            │
│                                                              │
│   heart.csv          ←── the real 10 MB data (in .gitignore) │
│   heart.csv.dvc      ←── tiny pointer file (tracked by Git)  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
              │                              │
              │ DVC manages                  │ Git manages
              ▼                              ▼
   ┌──────────────────┐          ┌──────────────────────┐
   │  Actual data in  │          │  heart.csv.dvc        │
   │  DVC cache, then │          │  (hash: a1b2c3...)    │
   │  pushed to cloud │          │  committed to GitHub  │
   │  (S3/GCS/etc.)   │          │                       │
   └──────────────────┘          └──────────────────────┘
```

### The Division of Labor

| Responsibility | Handled by |
|---------------|-----------|
| Source code (`.py`, `.yaml`) | **Git** |
| The `.dvc` pointer files | **Git** |
| `dvc.yaml` pipeline definitions | **Git** |
| Large datasets | **DVC** |
| Trained models | **DVC** |
| Intermediate artifacts | **DVC** |
| Storing data in the cloud | **DVC** |

The beauty: when you check out an old Git commit, the `.dvc` pointer files come with it. Then `dvc checkout` reads those pointers and restores the **exact** matching data. Your code and data are always in sync.

---

## Part 3 — The Mental Model: Pointers, Cache, and Remotes

Three locations matter in DVC. Understanding these makes everything click.

```
┌────────────────┐   dvc add    ┌─────────────────┐   dvc push   ┌──────────────────┐
│  Workspace     │ ───────────► │  DVC Cache      │ ───────────► │  DVC Remote      │
│  (your files   │              │  (.dvc/cache)   │              │  (S3, GCS, GDrive│
│   you work on) │ ◄─────────── │  hidden, local  │ ◄─────────── │   SSH, local dir)│
│                │ dvc checkout │                 │   dvc pull   │                  │
└────────────────┘              └─────────────────┘              └──────────────────┘
```

- **Workspace** — your project folder where you actually see and edit files.
- **DVC Cache** — a hidden local store (`.dvc/cache`) where DVC keeps content-addressed copies of every version of your data. This is the local equivalent of `.git`.
- **DVC Remote** — cloud or remote storage (S3, Google Drive, Azure, GCS, SSH, even a network folder) where you back up and share the cache. This is the equivalent of GitHub for your data.

The parallel to Git is intentional and worth memorizing:

| Git | DVC |
|-----|-----|
| `git add` | `dvc add` |
| `git commit` | (the `.dvc` file is committed via Git) |
| `git push` | `dvc push` |
| `git pull` | `dvc pull` |
| `git checkout` | `dvc checkout` |
| `.git/` | `.dvc/cache` |
| GitHub | DVC remote (S3/GDrive/etc.) |

---

## Part 4 — Installation & Initializing DVC

### Install DVC

```bash
# Using pip (most common)
pip install dvc

# With support for a specific remote (install the one you need):
pip install "dvc[s3]"       # Amazon S3
pip install "dvc[gdrive]"   # Google Drive
pip install "dvc[gs]"       # Google Cloud Storage
pip install "dvc[azure]"    # Azure Blob Storage
pip install "dvc[ssh]"      # SSH/SFTP

# Or all remotes
pip install "dvc[all]"
```

```bash
# Verify
dvc --version
# Output: 3.48.0
```

### Initialize DVC in a Git Repository

DVC requires an existing Git repo. So the order is always: **Git first, DVC second.**

```bash
# Create and enter the project
mkdir heart_disease_classifier
cd heart_disease_classifier

# Initialize Git FIRST
git init

# Then initialize DVC
dvc init
```

**What `dvc init` creates:**
```
.dvc/
├── .gitignore       ← tells Git to ignore the DVC cache
├── config           ← DVC configuration (remotes, settings)
.dvcignore           ← like .gitignore but for DVC
```

```bash
# DVC stages these new files for you. Commit them with Git:
git status
```

```
Changes to be committed:
        new file:   .dvc/.gitignore
        new file:   .dvc/config
        new file:   .dvcignore
```

```bash
git commit -m "Initialize DVC"
```

You now have a project tracked by both Git (code) and DVC (data).

---

## Part 5 — Tracking Your First Dataset

Let's get the Heart Disease dataset. It's a classic UCI dataset with 13 features (age, cholesterol, blood pressure, etc.) and a binary target (presence of heart disease).

```bash
# Create a data directory
mkdir data

# For this tutorial, download a heart disease dataset CSV into data/
# (In practice you might use your own data, or pull from a source)
# We'll assume data/heart.csv exists with columns:
# age, sex, cp, trestbps, chol, fbs, restecg, thalach,
# exang, oldpeak, slope, ca, thal, target
```

A peek at the data structure:

```
age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target
63,1,3,145,233,1,0,150,0,2.3,0,0,1,1
37,1,2,130,250,0,1,187,0,3.5,0,0,2,1
41,0,1,130,204,0,0,172,0,1.4,2,0,2,1
...
```

### Track It With DVC

```bash
dvc add data/heart.csv
```

**Output:**
```
100% Adding...|████████████████████████|1/1 [00:00, 45.21file/s]

To track the changes with git, run:
        git add data/heart.csv.dvc data/.gitignore

To enable auto staging, run:
        dvc config core.autostage true
```

**What just happened?** DVC did three things:
1. Moved the real `heart.csv` content into the DVC cache (`.dvc/cache`)
2. Created `data/heart.csv.dvc` — the tiny pointer file
3. Added `data/heart.csv` to a `.gitignore` so Git ignores the real file

Let's look at the pointer file:

```bash
cat data/heart.csv.dvc
```

```yaml
outs:
- md5: a1b2c3d4e5f6789012345678abcdef00
  size: 11328
  hash: md5
  path: heart.csv
```

That `md5` hash is the fingerprint of your exact data. If even one value changes, the hash changes.

### Commit the Pointer With Git

```bash
git add data/heart.csv.dvc data/.gitignore
git commit -m "Track heart disease dataset with DVC"
```

Now Git knows about the *pointer*, and DVC knows about the *data*. They're linked.

---

## Part 6 — Setting Up Remote Storage

The DVC cache is local. To back up your data and share it with teammates, you push it to a **remote**. Let's use a few examples.

### Option A: Local Directory Remote (Great for Learning)

```bash
# Use a local folder as a "remote" (simulates cloud, good for practice)
mkdir -p /tmp/dvc-remote
dvc remote add -d myremote /tmp/dvc-remote
```

### Option B: Amazon S3

```bash
dvc remote add -d myremote s3://my-bucket/heart-disease-data
# Configure credentials via AWS CLI or environment variables
```

### Option C: Google Drive

```bash
dvc remote add -d myremote gdrive://your-folder-id
```

The `-d` flag makes it the **default** remote.

```bash
# Commit the remote config (it's stored in .dvc/config)
git add .dvc/config
git commit -m "Configure DVC remote storage"
```

### Push Data to the Remote

```bash
dvc push
```

**Output:**
```
1 file pushed
```

Your data is now safely backed up. A teammate who clones the Git repo can run `dvc pull` to download the exact same data.

```bash
# A teammate's workflow:
git clone <your-repo-url>
cd heart_disease_classifier
dvc pull          # downloads the actual data files from the remote
```

---

## Part 7 — Building a Reproducible DVC Pipeline

This is where DVC becomes truly powerful. Instead of running scripts manually and hoping you remember the order, you define a **pipeline** — a graph of stages that DVC runs in the correct order and re-runs only when inputs change.

Let's build the project code first, then wire it into a pipeline.

### Step 7.1 — Project Code

**`src/preprocess.py`** — clean and split the data:

```python
"""preprocess.py — Load, clean, and split the heart disease data."""
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split
import os

# Load parameters from params.yaml
with open("params.yaml") as f:
    params = yaml.safe_load(f)

test_size = params["preprocess"]["test_size"]
random_state = params["preprocess"]["random_state"]

# Load raw data
df = pd.read_csv("data/heart.csv")

# Basic cleaning: drop duplicates, handle any missing values
df = df.drop_duplicates()
df = df.dropna()

# Split features and target
X = df.drop(columns=["target"])
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=random_state, stratify=y
)

# Save processed splits
os.makedirs("data/processed", exist_ok=True)
X_train.to_csv("data/processed/X_train.csv", index=False)
X_test.to_csv("data/processed/X_test.csv", index=False)
y_train.to_csv("data/processed/y_train.csv", index=False)
y_test.to_csv("data/processed/y_test.csv", index=False)

print(f"Preprocessing complete. Train: {len(X_train)}, Test: {len(X_test)}")
```

**`src/train.py`** — train the model:

```python
"""train.py — Train a Random Forest on the processed data."""
import pandas as pd
import yaml
import joblib
import os
from sklearn.ensemble import RandomForestClassifier

with open("params.yaml") as f:
    params = yaml.safe_load(f)

n_estimators = params["train"]["n_estimators"]
max_depth = params["train"]["max_depth"]
random_state = params["train"]["random_state"]

X_train = pd.read_csv("data/processed/X_train.csv")
y_train = pd.read_csv("data/processed/y_train.csv").values.ravel()

model = RandomForestClassifier(
    n_estimators=n_estimators,
    max_depth=max_depth,
    random_state=random_state,
    n_jobs=-1,
)
model.fit(X_train, y_train)

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.pkl")
print(f"Model trained with {n_estimators} trees, max_depth={max_depth}")
```

**`src/evaluate.py`** — evaluate and write metrics:

```python
"""evaluate.py — Evaluate the model and save metrics."""
import pandas as pd
import joblib
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

X_test = pd.read_csv("data/processed/X_test.csv")
y_test = pd.read_csv("data/processed/y_test.csv").values.ravel()

model = joblib.load("models/model.pkl")
y_pred = model.predict(X_test)

metrics = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred),
    "recall": recall_score(y_test, y_pred),
    "f1": f1_score(y_test, y_pred),
}

with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

print("Metrics:", metrics)
```

### Step 7.2 — Parameters File

DVC encourages keeping hyperparameters in a `params.yaml` file (not hardcoded). This makes experiments trackable.

**`params.yaml`:**

```yaml
preprocess:
  test_size: 0.2
  random_state: 42

train:
  n_estimators: 100
  max_depth: 5
  random_state: 42
```

### Step 7.3 — Define the Pipeline Stages

Now we connect everything into a pipeline using `dvc stage add`. Each stage declares its dependencies (`-d`), parameters (`-p`), and outputs (`-o`).

```bash
# Stage 1: preprocess
dvc stage add -n preprocess \
  -d src/preprocess.py -d data/heart.csv \
  -p preprocess.test_size,preprocess.random_state \
  -o data/processed \
  python src/preprocess.py

# Stage 2: train
dvc stage add -n train \
  -d src/train.py -d data/processed \
  -p train.n_estimators,train.max_depth,train.random_state \
  -o models/model.pkl \
  python src/train.py

# Stage 3: evaluate
dvc stage add -n evaluate \
  -d src/evaluate.py -d models/model.pkl -d data/processed \
  -M metrics.json \
  python src/evaluate.py
```

This generates a **`dvc.yaml`** file describing the whole pipeline:

```yaml
stages:
  preprocess:
    cmd: python src/preprocess.py
    deps:
      - src/preprocess.py
      - data/heart.csv
    params:
      - preprocess.test_size
      - preprocess.random_state
    outs:
      - data/processed
  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed
    params:
      - train.n_estimators
      - train.max_depth
      - train.random_state
    outs:
      - models/model.pkl
  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/model.pkl
      - data/processed
    metrics:
      - metrics.json
```

The `-M` flag marks `metrics.json` as a metrics file (DVC can compare these across runs).

### Step 7.4 — Run the Pipeline

```bash
dvc repro
```

**Output:**
```
Running stage 'preprocess':
> python src/preprocess.py
Preprocessing complete. Train: 242, Test: 61

Running stage 'train':
> python src/train.py
Model trained with 100 trees, max_depth=5

Running stage 'evaluate':
> python src/evaluate.py
Metrics: {'accuracy': 0.85, 'precision': 0.86, 'recall': 0.84, 'f1': 0.85}

Generating lock file 'dvc.lock'
```

DVC created **`dvc.lock`** — a file recording the exact hashes of all inputs and outputs from this run. This is what guarantees reproducibility.

### Step 7.5 — The Magic of `dvc repro`

Run it again without changing anything:

```bash
dvc repro
```

```
Stage 'preprocess' didn't change, skipping
Stage 'train' didn't change, skipping
Stage 'evaluate' didn't change, skipping
```

DVC is smart: it detected nothing changed and skipped everything. Now change a hyperparameter in `params.yaml` (e.g., `max_depth: 10`) and re-run:

```bash
dvc repro
```

```
Stage 'preprocess' didn't change, skipping
Running stage 'train':           ← only re-runs what's affected!
...
Running stage 'evaluate':
...
```

It skipped preprocessing (unaffected) and only re-ran training and evaluation. This dependency-aware re-running saves enormous time on large pipelines.

### Step 7.6 — Commit the Pipeline

```bash
git add dvc.yaml dvc.lock params.yaml src/ .gitignore metrics.json
git commit -m "Add DVC pipeline: preprocess -> train -> evaluate"

# Push data/model outputs to DVC remote
dvc push
```

---

## Part 8 — Versioning Data + Code Together

Here is the core workflow that ties Git and DVC into one coherent system. Whenever you make a change, you commit to **both**.

```
┌──────────────────────────────────────────────────────────┐
│  Standard Git + DVC commit workflow                        │
│                                                            │
│  1. [make changes to code, data, or params]               │
│  2. dvc repro             ← rebuild affected pipeline      │
│  3. git add <code, dvc.yaml, dvc.lock, .dvc files>        │
│  4. git commit -m "..."   ← version the pointers + code   │
│  5. dvc push              ← back up the actual data/models │
│  6. git push              ← back up the code + pointers    │
└──────────────────────────────────────────────────────────┘
```

The golden rule: **`git push` and `dvc push` go together.** Git pushes the lightweight pointers and code; DVC pushes the heavy data and models. If you only do one, your teammate gets a broken state.

---

## Part 9 — Experiments, Metrics, and Params

DVC has first-class support for ML experimentation. Let's compare model versions properly.

### Comparing Metrics Across Versions

```bash
# Show current metrics
dvc metrics show
```

```
Path           accuracy   precision   recall    f1
metrics.json   0.85       0.86        0.84      0.85
```

### Tracking Parameters

```bash
dvc params diff
```

```
Path          Param                  HEAD    workspace
params.yaml   train.max_depth        5       10
```

### Running Quick Experiments with `dvc exp`

The `dvc exp` commands let you try variations without cluttering Git history:

```bash
# Run an experiment changing a parameter on the fly
dvc exp run --set-param train.n_estimators=200

# Run another with different depth
dvc exp run --set-param train.max_depth=8

# Compare all experiments in a table
dvc exp show
```

**Output:**
```
 Experiment          n_estimators   max_depth   accuracy   f1
 ─────────────────────────────────────────────────────────────
 workspace           200            8           0.88       0.87
 main                 100            5           0.85       0.85
 ├── exp-a1b2c        200            5           0.87       0.86
 ├── exp-c3d4e        100            8           0.86       0.85
 └── exp-e5f6g        200            8           0.88       0.87
```

This table is the single most useful thing about DVC for ML — you see at a glance which hyperparameters gave which results.

```bash
# Promote the best experiment to your workspace
dvc exp apply exp-e5f6g

# Then commit it properly
git add dvc.lock params.yaml metrics.json
git commit -m "Adopt best config: 200 trees, max_depth=8 (acc 0.88)"
dvc push
git push
```

---

## Part 10 — Full Heart Disease Project Walkthrough

Let's tie everything together in one continuous sequence, simulating a real project from scratch.

### Act 1: Setup

```bash
mkdir heart_disease_classifier && cd heart_disease_classifier
git init
dvc init
git commit -m "Initialize Git and DVC"
```

### Act 2: Add the Data

```bash
mkdir data
# (place heart.csv in data/)
dvc add data/heart.csv
git add data/heart.csv.dvc data/.gitignore
git commit -m "Add heart disease dataset (v1, 303 rows)"

# Configure and push to remote
mkdir -p /tmp/dvc-remote
dvc remote add -d myremote /tmp/dvc-remote
git add .dvc/config
git commit -m "Configure DVC remote"
dvc push
```

### Act 3: Build the Code and Pipeline

```bash
mkdir src
# (create src/preprocess.py, src/train.py, src/evaluate.py, params.yaml as shown above)

# Define pipeline stages
dvc stage add -n preprocess -d src/preprocess.py -d data/heart.csv \
  -p preprocess.test_size,preprocess.random_state -o data/processed \
  python src/preprocess.py

dvc stage add -n train -d src/train.py -d data/processed \
  -p train.n_estimators,train.max_depth,train.random_state -o models/model.pkl \
  python src/train.py

dvc stage add -n evaluate -d src/evaluate.py -d models/model.pkl -d data/processed \
  -M metrics.json python src/evaluate.py

# Run it
dvc repro

# Commit everything
git add dvc.yaml dvc.lock params.yaml src/ .gitignore metrics.json
git commit -m "Add full ML pipeline, baseline accuracy 0.85"
dvc push
```

### Act 4: The Data Changes (this is where DVC shines)

**Scenario:** Your data team sends you an updated dataset with 500 more patient records. You need to retrain — but you also want to keep the old data version reproducible.

```bash
# Replace the data file with the new version
# (copy the new, larger heart.csv into data/)

# Tell DVC the tracked file changed
dvc add data/heart.csv
```

```
...
To track the changes with git, run:
        git add data/heart.csv.dvc
```

```bash
# The pointer file's hash changed. Commit the new pointer:
git add data/heart.csv.dvc
git commit -m "Update dataset to v2 (added 500 records)"

# Re-run the pipeline on new data
dvc repro
```

```
Running stage 'preprocess':     ← data changed, so everything reruns
...
Running stage 'train':
...
Running stage 'evaluate':
Metrics: {'accuracy': 0.89, ...}    ← more data, better accuracy
```

```bash
git add dvc.lock metrics.json
git commit -m "Retrain on v2 data, accuracy improved to 0.89"
dvc push
git push
```

### Act 5: Tag the Releases

```bash
git tag -a v1.0 -m "Baseline model on 303-record dataset, acc 0.85"
git tag -a v2.0 -m "Model on expanded 800-record dataset, acc 0.89"
git push --tags
```

---

## Part 11 — Switching Between Versions (The Payoff)

This is the moment all the work pays off. Suppose your manager asks: *"Can you reproduce the exact model and data from the v1.0 release that we showed the client?"*

With Git alone, you'd only get the code back. With Git + DVC, you get **everything** — code, data, and model — in exact sync.

```bash
# Step 1: Check out the old code AND pointer files via Git
git checkout v1.0
```

At this point your `.dvc` and `dvc.lock` files now describe the v1.0 state, but your actual `data/heart.csv` on disk is still the v2 version. The pointers and the real files are mismatched. So:

```bash
# Step 2: Tell DVC to restore the data matching these pointers
dvc checkout
```

```
M       data/heart.csv          ← restored to the 303-record version!
M       data/processed/
M       models/model.pkl        ← the original v1 model is back
```

Now your entire workspace — code, the exact 303-row dataset, and the original trained model — is precisely as it was at the v1.0 release. You can run, inspect, or demo it.

```bash
# Verify
dvc metrics show
# accuracy: 0.85   ← the original v1 numbers, reproduced exactly
```

To return to the latest:

```bash
git checkout main
dvc checkout
```

> **The mental model to lock in:** `git checkout` switches the *pointers and code*; `dvc checkout` makes the *actual data and models* match those pointers. Always run them as a pair when time-traveling.

---

## The Complete Git + DVC Cheat Sheet

```
SETUP
─────────────────────────────────────────────
git init                          Initialize Git
dvc init                          Initialize DVC (needs Git first)
dvc remote add -d myremote <url>  Set default remote storage

TRACKING DATA
─────────────────────────────────────────────
dvc add data/file.csv             Start tracking a data file
git add data/file.csv.dvc         Commit the pointer (with Git)
dvc add data/file.csv             Re-run after data changes

PIPELINES
─────────────────────────────────────────────
dvc stage add -n <name> ...       Define a pipeline stage
dvc repro                         Run pipeline (only changed stages)
dvc dag                           Visualize the pipeline graph

SYNCING
─────────────────────────────────────────────
dvc push                          Upload data/models to remote
dvc pull                          Download data/models from remote
git push                          Upload code + pointers
git pull                          Download code + pointers

EXPERIMENTS & METRICS
─────────────────────────────────────────────
dvc exp run --set-param k=v       Run a quick experiment
dvc exp show                      Compare experiments in a table
dvc exp apply <exp-id>            Adopt an experiment's results
dvc metrics show                  Show current metrics
dvc metrics diff                  Compare metrics vs last commit
dvc params diff                   Compare params vs last commit

TIME TRAVEL (always run as a pair)
─────────────────────────────────────────────
git checkout <tag/commit>         Switch code + pointers
dvc checkout                      Restore matching data + models
```

---

## What Goes Where: Final Reference

| File / Folder | Tracked by Git? | Tracked by DVC? | In `.gitignore`? |
|---------------|:---------------:|:---------------:|:----------------:|
| `src/*.py` | ✅ | ❌ | ❌ |
| `params.yaml` | ✅ | ❌ | ❌ |
| `dvc.yaml` | ✅ | ❌ | ❌ |
| `dvc.lock` | ✅ | ❌ | ❌ |
| `data/heart.csv.dvc` | ✅ | ❌ | ❌ |
| `data/heart.csv` (real data) | ❌ | ✅ | ✅ (auto by DVC) |
| `data/processed/` | ❌ | ✅ | ✅ (pipeline output) |
| `models/model.pkl` | ❌ | ✅ | ✅ (pipeline output) |
| `metrics.json` | ✅ | (tracked as metric) | ❌ |
| `.dvc/cache` | ❌ | (is the cache) | ✅ (auto by DVC) |

---

## Summary

You now understand how Git and DVC form a complete versioning system for ML:

✅ **Why Git alone fails** for data and models — and exactly what DVC adds  
✅ **The pointer model** — Git tracks tiny `.dvc` files, DVC tracks the heavy data  
✅ **Cache and remotes** — how data is stored locally and backed up to the cloud  
✅ **DVC pipelines** — reproducible, dependency-aware `dvc repro` workflows  
✅ **Experiments and metrics** — comparing model versions with `dvc exp show`  
✅ **Time travel** — restoring any past code+data+model combination with `git checkout` + `dvc checkout`  

### Where to Go Next

- **CI/CD for ML** — use **CML (Continuous Machine Learning)** with GitHub Actions to auto-train and post metrics on every pull request
- **DVC Studio** — a web dashboard for visualizing experiments and metrics across your team
- **Data registries** — share versioned datasets across multiple projects with `dvc import`
- **Model registry** — promote and deploy specific model versions to production

You can now version an entire ML project end-to-end — every line of code and every byte of data — and reproduce any past state on demand. This is the foundation of professional, reproducible machine learning.
