# Article 2: Git in Action — Iris Classification Project

*A complete hands-on walkthrough of Git and GitHub using a real ML project*

---

## Introduction

In Article 1 you learned every Git command individually. Now we build muscle memory by using all of them in a realistic ML project scenario. We will build a simple but complete Iris flower classification project, and at every step we will pause and explain the Git operations in context — exactly as you would use them on a real job.

By the end of this article you will have:
- A fully version-controlled ML project on GitHub
- Experience with commits, branches, merging, reverting, stashing, and pull requests
- A workflow you can immediately apply to your own projects

---

## The Project We Are Building

**Task:** Classify Iris flowers into 3 species (Setosa, Versicolor, Virginica) based on sepal and petal measurements.

**Tech stack:** Python, scikit-learn, pandas, matplotlib

**Final project structure:**

```
iris_classifier/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── iris.csv              (ignored by git)
├── src/
│   ├── __init__.py
│   ├── preprocess.py
│   ├── train.py
│   └── evaluate.py
├── notebooks/
│   └── exploration.ipynb
└── models/                   (ignored by git)
    └── trained_model.pkl
```

---

## Act 1: Project Initialization

### Step 1.1 — Create the Project and Initialize Git

Open your terminal and run:

```bash
# Create the project directory and navigate into it
mkdir iris_classifier
cd iris_classifier

# Initialize as a Git repository
git init
```

**Output:**
```
Initialized empty Git repository in /iris_classifier/.git/
```

You now have an empty Git repository. Nothing is tracked yet.

```bash
# Confirm Git is watching (status on empty repo)
git status
```

**Output:**
```
On branch main

No commits yet

nothing to commit (create/copy files and start working)
```

---

### Step 1.2 — Create the .gitignore First (Always Do This First!)

This is a habit you must build: **create `.gitignore` before you create anything else.** If you track a file by accident and commit it, removing it from history is painful.

```bash
# Create .gitignore
touch .gitignore
```

Open `.gitignore` in any editor and add:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.Python
venv/
.venv/
*.egg-info/

# Jupyter Notebooks
.ipynb_checkpoints/

# Data files (store separately — e.g., DVC, S3, shared drive)
data/
*.csv
*.tsv

# Trained models (can be large)
models/
*.pkl
*.joblib
*.h5

# Secrets
.env
*.key

# OS
.DS_Store
```

```bash
# Check Git can see the new file
git status
```

**Output:**
```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .gitignore

nothing added to commit but untracked files present
```

Stage and commit:

```bash
git add .gitignore
git commit -m "Add .gitignore for Python and ML artifacts"
```

**Output:**
```
[main (root-commit) 4a1b2c3] Add .gitignore for Python and ML artifacts
 1 file changed, 20 insertions(+)
 create mode 100644 .gitignore
```

🎉 First commit made! Notice:
- `root-commit` means this is the first-ever commit in this repo
- `4a1b2c3` is the short SHA (your SHA will be different)

---

### Step 1.3 — Create the README

A README is the front page of your project on GitHub. Create `README.md`:

```markdown
# Iris Flower Classifier

A machine learning project that classifies Iris flowers into 3 species
(Setosa, Versicolor, Virginica) using the classic Iris dataset.

## Project Structure
- `src/` — Source code for preprocessing, training, and evaluation
- `notebooks/` — Exploratory data analysis
- `requirements.txt` — Python dependencies

## Setup
```bash
pip install -r requirements.txt
```

## Usage
```bash
python src/train.py
python src/evaluate.py
```

## Results
| Model | Test Accuracy |
|-------|--------------|
| Logistic Regression | TBD |
| Random Forest | TBD |
```

```bash
git add README.md
git commit -m "Add project README with structure and setup instructions"
```

---

### Step 1.4 — Create Project Structure and requirements.txt

```bash
# Create directory structure
mkdir -p src notebooks data models

# Create placeholder files so Git tracks the directories
touch src/__init__.py
touch notebooks/.gitkeep    # empty placeholder so git tracks the folder

# Create requirements.txt
cat > requirements.txt << 'EOF'
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.4
matplotlib==3.8.2
seaborn==0.13.2
joblib==1.3.2
EOF
```

```bash
git add requirements.txt src/__init__.py notebooks/.gitkeep
git commit -m "Add project structure and Python dependencies"
```

**Check the log so far:**

```bash
git log --oneline
```

**Output:**
```
9d3f1a2 Add project structure and Python dependencies
7b2e4c1 Add project README with structure and setup instructions
4a1b2c3 Add .gitignore for Python and ML artifacts
```

Your project history is already telling a clean story.

---

## Act 2: Building the Baseline Model (on `main`)

### Step 2.1 — Write the Preprocessing Code

Create `src/preprocess.py`:

```python
"""
preprocess.py — Load and prepare the Iris dataset for training.
"""

import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


def load_data():
    """Load the Iris dataset and return as a DataFrame."""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['target'] = iris.target
    df['species'] = df['target'].map({
        0: 'setosa',
        1: 'versicolor',
        2: 'virginica'
    })
    return df


def split_data(df, test_size=0.2, random_state=42):
    """Split into train/test sets."""
    X = df[['sepal length (cm)', 'sepal width (cm)',
            'petal length (cm)', 'petal width (cm)']]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y        # ensures balanced class distribution in splits
    )

    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    df = load_data()
    print(df.head())
    print(f"Dataset shape: {df.shape}")
    split_data(df)
```

```bash
git add src/preprocess.py
git commit -m "Add data loading and train-test split with stratification"
```

---

### Step 2.2 — Write the Baseline Training Code

Create `src/train.py`:

```python
"""
train.py — Train a Logistic Regression baseline model.
"""

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os
from preprocess import load_data, split_data


def train_model(X_train, y_train):
    """Build and train a logistic regression pipeline."""
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(
            max_iter=200,
            random_state=42
        ))
    ])
    pipeline.fit(X_train, y_train)
    return pipeline


def save_model(model, path='models/logistic_regression.pkl'):
    """Save trained model to disk."""
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, path)
    print(f"Model saved to {path}")


if __name__ == "__main__":
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)

    print("Training logistic regression...")
    model = train_model(X_train, y_train)

    save_model(model)
    print("Training complete!")
```

```bash
git add src/train.py
git commit -m "Add logistic regression baseline with StandardScaler pipeline"
```

---

### Step 2.3 — Write the Evaluation Code

Create `src/evaluate.py`:

```python
"""
evaluate.py — Evaluate the trained model on the test set.
"""

import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns
from preprocess import load_data, split_data


def evaluate_model(model, X_test, y_test):
    """Print evaluation metrics."""
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n{'='*40}")
    print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"{'='*40}\n")

    print("Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=['setosa', 'versicolor', 'virginica']
    ))

    return y_pred, accuracy


def plot_confusion_matrix(y_test, y_pred):
    """Plot and save confusion matrix."""
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=['setosa', 'versicolor', 'virginica'],
        yticklabels=['setosa', 'versicolor', 'virginica']
    )
    plt.title('Confusion Matrix — Logistic Regression')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=150)
    print("Confusion matrix saved.")


if __name__ == "__main__":
    model = joblib.load('models/logistic_regression.pkl')

    df = load_data()
    _, X_test, _, y_test = split_data(df)

    y_pred, accuracy = evaluate_model(model, X_test, y_test)
    plot_confusion_matrix(y_test, y_pred)
```

```bash
git add src/evaluate.py
git commit -m "Add model evaluation with accuracy, classification report, and confusion matrix"
```

**Check history:**

```bash
git log --oneline
```

```
e5c1d23 Add model evaluation with accuracy, classification report, and confusion matrix
3f8b7a4 Add logistic regression baseline with StandardScaler pipeline
1d2e6c5 Add data loading and train-test split with stratification
9d3f1a2 Add project structure and Python dependencies
7b2e4c1 Add project README with structure and setup instructions
4a1b2c3 Add .gitignore for Python and ML artifacts
```

You now have a complete baseline model with 6 clean, meaningful commits.

---

## Act 3: Experimenting with a New Model (Feature Branch)

**Scenario:** Your baseline logistic regression gets 97% accuracy. You want to try a Random Forest model to see if it performs better. You should do this on a **feature branch** so `main` stays clean and working.

### Step 3.1 — Create a Feature Branch

```bash
# Create and switch to a new branch
git switch -c feature/random-forest-model
```

**Output:**
```
Switched to a new branch 'feature/random-forest-model'
```

```bash
# Confirm we're on the right branch
git branch
```

**Output:**
```
* feature/random-forest-model     ← asterisk shows current branch
  main
```

Notice: The new branch is a **copy of `main`** at this point. All 6 commits exist here too. But any new commits you make will only go on this branch.

---

### Step 3.2 — Add the Random Forest Training Script

Create `src/train_rf.py`:

```python
"""
train_rf.py — Train a Random Forest classifier.
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import joblib
import numpy as np
import os
from preprocess import load_data, split_data


def train_random_forest(X_train, y_train, n_estimators=100, max_depth=None):
    """Build and train a Random Forest pipeline."""
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1          # use all CPU cores
        ))
    ])

    # Cross-validation on training set for reliable performance estimate
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='accuracy')
    print(f"5-Fold CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Fit on full training set
    pipeline.fit(X_train, y_train)
    return pipeline


def save_model(model, path='models/random_forest.pkl'):
    """Save trained model to disk."""
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, path)
    print(f"Model saved to {path}")


if __name__ == "__main__":
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)

    print("Training Random Forest with cross-validation...")
    model = train_random_forest(X_train, y_train, n_estimators=100)

    save_model(model)
    print("Random Forest training complete!")
```

```bash
git add src/train_rf.py
git commit -m "Add Random Forest classifier with 5-fold cross-validation"
```

---

### Step 3.3 — Update evaluate.py to Support Both Models

We'll modify `src/evaluate.py` to accept a model path argument:

```bash
# First, view what changed since branching
git diff main feature/random-forest-model
```

Now edit `src/evaluate.py` — change the `if __name__ == "__main__":` block:

```python
if __name__ == "__main__":
    import sys

    model_path = sys.argv[1] if len(sys.argv) > 1 else 'models/logistic_regression.pkl'
    model = joblib.load(model_path)

    df = load_data()
    _, X_test, _, y_test = split_data(df)

    y_pred, accuracy = evaluate_model(model, X_test, y_test)
    plot_confusion_matrix(y_test, y_pred)
```

```bash
# See the exact change
git diff src/evaluate.py
```

**Sample output:**
```diff
-    model = joblib.load('models/logistic_regression.pkl')
+    import sys
+    model_path = sys.argv[1] if len(sys.argv) > 1 else 'models/logistic_regression.pkl'
+    model = joblib.load(model_path)
```

Stage and commit:

```bash
git add src/evaluate.py
git commit -m "Make evaluate.py accept model path as CLI argument"
```

---

### Step 3.4 — View Branch Differences

```bash
# See commits that are in feature branch but NOT in main
git log main..feature/random-forest-model --oneline
```

**Output:**
```
9a8b3c1 Make evaluate.py accept model path as CLI argument
7c4d2e5 Add Random Forest classifier with 5-fold cross-validation
```

```bash
# Visual history of all branches
git log --oneline --graph --all
```

**Output:**
```
* 9a8b3c1 (HEAD -> feature/random-forest-model) Make evaluate.py accept model path as CLI argument
* 7c4d2e5 Add Random Forest classifier with 5-fold cross-validation
* e5c1d23 (main) Add model evaluation with accuracy, classification report, and confusion matrix
* 3f8b7a4 Add logistic regression baseline with StandardScaler pipeline
* 1d2e6c5 Add data loading and train-test split with stratification
* 9d3f1a2 Add project structure and Python dependencies
* 7b2e4c1 Add project README with structure and setup instructions
* 4a1b2c3 Add .gitignore for Python and ML artifacts
```

Notice how `main` and `feature/random-forest-model` diverge from commit `e5c1d23`.

---

## Act 4: Merging the Feature Branch

The Random Forest works great. Time to bring it into `main`.

### Step 4.1 — Switch to Main and Merge

```bash
# Switch back to main
git switch main

# Merge the feature branch
git merge feature/random-forest-model
```

**Output (fast-forward merge — because main had no new commits):**
```
Updating e5c1d23..9a8b3c1
Fast-forward
 src/evaluate.py  | 5 +++--
 src/train_rf.py  | 45 +++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 48 insertions(+), 2 deletions(-)
 create mode 100644 src/train_rf.py
```

```bash
# Clean up: delete the feature branch (it's merged, we don't need it)
git branch -d feature/random-forest-model
```

```bash
git log --oneline
```

```
9a8b3c1 (HEAD -> main) Make evaluate.py accept model path as CLI argument
7c4d2e5 Add Random Forest classifier with 5-fold cross-validation
e5c1d23 Add model evaluation with accuracy, classification report, and confusion matrix
...
```

---

## Act 5: Simulating a Bug and Rolling It Back

**Scenario:** A junior team member (or you on a bad day) introduced a bug — they accidentally removed `stratify=y` from the train-test split, causing class imbalance. This bug was committed and pushed. You need to fix it.

### Step 5.1 — Introduce the Bug (to practice reverting)

Edit `src/preprocess.py` — find the `train_test_split` call and remove `stratify=y`:

```python
# BUGGY VERSION — missing stratify=y
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=test_size,
    random_state=random_state
    # stratify=y  ← accidentally removed!
)
```

```bash
git add src/preprocess.py
git commit -m "Update train-test split parameters"
# (vague message — a red flag for code review!)
```

Now there is a bug in your history. Let's say you realize the model accuracy dropped.

---

### Step 5.2 — Find the Bug with `git log` and `git diff`

```bash
# See recent commits
git log --oneline -5
```

```
b3c2d1e (HEAD -> main) Update train-test split parameters
9a8b3c1 Make evaluate.py accept model path as CLI argument
...
```

```bash
# See exactly what changed in that commit
git show b3c2d1e
```

**Output:**
```diff
-        stratify=y
```

Found it. The `stratify=y` was removed.

---

### Step 5.3 — Revert the Bug (Safe Method)

Since this commit may already be pushed to GitHub (shared with others), we use `git revert` instead of `git reset`. Revert creates a NEW commit that undoes the changes, leaving history intact.

```bash
git revert HEAD --no-edit
```

**Output:**
```
[main 4d3e2c1] Revert "Update train-test split parameters"
 1 file changed, 1 insertion(+), 1 deletion(-)
```

```bash
git log --oneline -5
```

```
4d3e2c1 (HEAD -> main) Revert "Update train-test split parameters"
b3c2d1e Update train-test split parameters    ← bug commit still in history
9a8b3c1 Make evaluate.py accept model path as CLI argument
```

Notice the bug commit is still in the log. `git revert` does not hide history — it adds a "correction" commit. This is honest, auditable, and safe for shared branches.

---

## Act 6: The Stash — Switching Context Mid-Work

**Scenario:** You are halfway through writing a Support Vector Machine (SVM) experiment. Suddenly your manager pings you: "The preprocessing pipeline is failing in production — drop everything and fix it now!"

Your SVM code is half-written and you cannot commit unfinished work.

### Step 6.1 — Stash Half-Done Work

```bash
# Create a partial file (half-done SVM code)
cat > src/train_svm.py << 'EOF'
"""
train_svm.py — SVM classifier (work in progress!)
"""
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
# TODO: add cross-validation
# TODO: add hyperparameter grid
def train_svm(X_train, y_train):
EOF

# Check status
git status
```

```
On branch main
Untracked files:
        src/train_svm.py
```

```bash
# Stash it with a meaningful description
git stash push -m "WIP: SVM classifier — halfway through, no CV yet"

# Confirm working directory is now clean
git status
```

```
On branch main
nothing to commit, working tree clean
```

```bash
# Your stash is saved
git stash list
```

```
stash@{0}: On main: WIP: SVM classifier — halfway through, no CV yet
```

---

### Step 6.2 — Fix the Production Bug

```bash
# Create hotfix branch for the fix
git switch -c hotfix/fix-feature-scaling-bug
```

Make your fix (imagine fixing a bug in `preprocess.py`):

```python
# Fix: ensure we return copies, not views, to prevent unexpected mutations
X_train = X_train.copy()
X_test = X_test.copy()
```

```bash
git add src/preprocess.py
git commit -m "Fix: return copies from split_data to prevent mutation bugs"

# Merge the fix back to main immediately
git switch main
git merge hotfix/fix-feature-scaling-bug
git branch -d hotfix/fix-feature-scaling-bug
```

---

### Step 6.3 — Restore Stashed Work

```bash
# Pop the stash to restore your half-done SVM code
git stash pop
```

**Output:**
```
On branch main
Untracked files:
        src/train_svm.py

Dropped stash@{0}: On main: WIP: SVM classifier — halfway through, no CV yet
```

Your SVM file is back exactly where you left it. Resume your work.

---

## Act 7: Pushing to GitHub and Opening a Pull Request

### Step 7.1 — Create a GitHub Repository

1. Go to **github.com** → **New repository**
2. Name it `iris-classifier`
3. Make it **Public** (so your portfolio is visible)
4. Do **NOT** initialize with README (you already have one locally)
5. Click **Create repository**

GitHub will show you the setup commands. Use these:

```bash
# Connect local repo to GitHub
git remote add origin git@github.com:YOUR_USERNAME/iris-classifier.git

# Verify
git remote -v
```

```
origin  git@github.com:YOUR_USERNAME/iris-classifier.git (fetch)
origin  git@github.com:YOUR_USERNAME/iris-classifier.git (push)
```

```bash
# Push all commits to GitHub
git push -u origin main
```

**Output:**
```
Enumerating objects: 28, done.
Counting objects: 100% (28/28), done.
...
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

Your project is now live on GitHub!

---

### Step 7.2 — Simulate a Pull Request Workflow

This simulates how teams collaborate. You will create a feature branch, push it, and open a PR.

```bash
# Create a branch to complete the SVM model
git switch -c feature/svm-classifier
```

Finish `src/train_svm.py`:

```python
"""
train_svm.py — Support Vector Machine classifier with grid search.
"""

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV, cross_val_score
import joblib
import os
from preprocess import load_data, split_data


def train_svm(X_train, y_train):
    """Train SVM with hyperparameter tuning via GridSearchCV."""
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', SVC(random_state=42, probability=True))
    ])

    # Hyperparameter grid
    param_grid = {
        'classifier__C': [0.1, 1, 10, 100],
        'classifier__kernel': ['rbf', 'linear'],
        'classifier__gamma': ['scale', 'auto']
    }

    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(X_train, y_train)

    print(f"Best Parameters: {grid_search.best_params_}")
    print(f"Best CV Score: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_


def save_model(model, path='models/svm_model.pkl'):
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, path)
    print(f"Model saved to {path}")


if __name__ == "__main__":
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)

    print("Training SVM with GridSearchCV...")
    model = train_svm(X_train, y_train)
    save_model(model)
```

```bash
git add src/train_svm.py
git commit -m "Add SVM classifier with GridSearchCV hyperparameter tuning"

# Push the feature branch to GitHub
git push -u origin feature/svm-classifier
```

**Output:**
```
...
 * [new branch]      feature/svm-classifier -> feature/svm-classifier
Branch 'feature/svm-classifier' set up to track remote branch 'feature/svm-classifier' from 'origin'.
```

Now on **GitHub.com**, navigate to your repository. You will see:

```
This branch has recent pushes — "Compare & pull request"
```

Click it, fill in the PR form:

```
Title: Add SVM classifier with GridSearchCV tuning

Description:
## What does this PR do?
Adds a Support Vector Machine (SVM) classifier with automated
hyperparameter tuning using GridSearchCV (5-fold CV).

## Hyperparameters explored
- C: [0.1, 1, 10, 100]
- kernel: ['rbf', 'linear']
- gamma: ['scale', 'auto']

## Testing
Run: python src/train_svm.py
```

After the PR is reviewed and approved → **Merge pull request** on GitHub.

Then locally:

```bash
# Pull the merged changes back to local main
git switch main
git pull origin main

# Delete the remote feature branch (GitHub may do this automatically)
git push origin --delete feature/svm-classifier

# Delete the local feature branch
git branch -d feature/svm-classifier
```

---

## Act 8: Tagging a Release

Your project now has 3 models. It is time to mark this as `v1.0`.

### Step 8.1 — Create a Tag

```bash
# Create an annotated tag with a message
git tag -a v1.0 -m "First stable release: Logistic Regression, Random Forest, and SVM classifiers"

# Verify
git tag
```

```
v1.0
```

```bash
# See the full tag info
git show v1.0
```

```
tag v1.0
Tagger: Your Name <you@example.com>
Date:   Mon Jan 15 10:30:00 2024 +0800

First stable release: Logistic Regression, Random Forest, and SVM classifiers

commit 9a8b3c1 (HEAD -> main, tag: v1.0)
...
```

```bash
# Push the tag to GitHub
git push origin v1.0
```

On GitHub, this creates a **Release** under the Releases section of your repo. Very professional for a portfolio.

---

## Act 9: Handling a Merge Conflict

**Scenario:** You and your teammate both edit `src/preprocess.py` at the same time. When you try to merge, Git finds a conflict.

### Step 9.1 — Simulate a Conflict

```bash
# Create two branches that both change the same line
git switch -c branch-a
```

Edit the `test_size` in `split_data()` in `preprocess.py`:

```python
# branch-a version
def split_data(df, test_size=0.25, random_state=42):  # changed to 0.25
```

```bash
git add src/preprocess.py
git commit -m "Change test split size to 25% for larger test set"
git switch main
```

```bash
# Create a second branch from main
git switch -c branch-b
```

Edit the same line differently:

```python
# branch-b version
def split_data(df, test_size=0.15, random_state=42):  # changed to 0.15
```

```bash
git add src/preprocess.py
git commit -m "Reduce test split size to 15% for more training data"
git switch main
```

```bash
# Merge branch-a first (succeeds)
git merge branch-a

# Merge branch-b (CONFLICT!)
git merge branch-b
```

**Output:**
```
Auto-merging src/preprocess.py
CONFLICT (content): Merge conflict in src/preprocess.py
Automatic merge failed; fix conflicts and then commit the result.
```

---

### Step 9.2 — Resolve the Conflict

```bash
git status
```

```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   src/preprocess.py
```

Open `src/preprocess.py`. The conflicted section looks like:

```python
<<<<<<< HEAD
def split_data(df, test_size=0.25, random_state=42):
=======
def split_data(df, test_size=0.15, random_state=42):
>>>>>>> branch-b
```

You discuss with your teammate and decide on 0.20 (the original default). Edit the file to:

```python
def split_data(df, test_size=0.20, random_state=42):
```

Remove the `<<<<<<<`, `=======`, and `>>>>>>>` markers entirely.

```bash
# Mark as resolved by staging it
git add src/preprocess.py

# Commit the resolution
git commit -m "Resolve merge conflict: keep default test_size=0.20"
```

```bash
# Clean up
git branch -d branch-a
git branch -d branch-b
```

---

## Act 10: Advanced — Reset to Undo Local Mistakes

**Scenario:** You made 3 commits locally that you realize are completely wrong. They have NOT been pushed yet, so it is safe to reset.

```bash
# View current commits
git log --oneline -5
```

```
d3e4f5a (HEAD -> main) WIP: bad experiment attempt 3
c2b3d4e WIP: bad experiment attempt 2
a1b2c3d WIP: bad experiment attempt 1
9a8b3c1 Add SVM classifier with GridSearchCV
```

You want to go back to `9a8b3c1` and throw away those 3 commits entirely:

```bash
# Hard reset — PERMANENTLY removes those 3 commits and all changes
git reset --hard 9a8b3c1
```

**Output:**
```
HEAD is now at 9a8b3c1 Add SVM classifier with GridSearchCV
```

Those 3 commits are gone. Your code is back to that state.

> ⚠️ Only do this when commits have NOT been pushed. If they were pushed, use `git revert` instead.

---

## Final Project: Full Git History

After all this practice, your project's history looks like:

```bash
git log --oneline --graph --all
```

```
* f1e2d3c (HEAD -> main, tag: v1.0) Resolve merge conflict: keep default test_size=0.20
* e4d5c6b Merge branch 'feature/svm-classifier'
|\
| * c7b8a9d Add SVM classifier with GridSearchCV hyperparameter tuning
|/
* b0a1f2e Fix: return copies from split_data to prevent mutation bugs
* 4d3e2c1 Revert "Update train-test split parameters"
* b3c2d1e Update train-test split parameters
* 9a8b3c1 Make evaluate.py accept model path as CLI argument
* 7c4d2e5 Add Random Forest classifier with 5-fold cross-validation
* e5c1d23 Add model evaluation with accuracy, classification report, and confusion matrix
* 3f8b7a4 Add logistic regression baseline with StandardScaler pipeline
* 1d2e6c5 Add data loading and train-test split with stratification
* 9d3f1a2 Add project structure and Python dependencies
* 7b2e4c1 Add project README with structure and setup instructions
* 4a1b2c3 Add .gitignore for Python and ML artifacts
```

This log tells the complete story of your project — what was built, what broke, what was fixed, and what experiments were run. This is professional-grade version control.

---

## Complete Workflow Reference Card

Here is the workflow you will repeat on every ML project:

```
Start of every work session:
─────────────────────────────
git switch main
git pull origin main

Starting new work:
─────────────────────────────
git switch -c feature/your-feature-name

During work (repeat many times):
─────────────────────────────
[edit files]
git status
git diff
git add <specific files>
git commit -m "Clear description of what and why"

Keeping your branch updated:
─────────────────────────────
git fetch origin
git rebase origin/main

Finishing:
─────────────────────────────
git push -u origin feature/your-feature-name
[open Pull Request on GitHub]
[merge after review]

After merge:
─────────────────────────────
git switch main
git pull origin main
git branch -d feature/your-feature-name

Emergency (discard all local changes):
─────────────────────────────
git stash           ← save first if needed
git restore .       ← nuclear discard

Emergency (undo a pushed commit):
─────────────────────────────
git revert HEAD
git push
```

---

## What to Do Next

Now that you have completed both articles, here are the next skills to build:

**Immediate next steps (apply to your own projects):**
1. Create a GitHub repo for your next ML project today
2. Practice the feature branch workflow on your existing projects
3. Write a proper `.gitignore` for every project

**Tools to learn after Git basics:**
- **DVC (Data Version Control)** — Git for data files and ML model artifacts. Works alongside Git.
- **GitHub Actions** — CI/CD automation (run tests, retrain models, deploy automatically on each push)
- **pre-commit hooks** — Automatically run code formatters and linters before every commit
- **Conventional Commits** — A structured commit message format for large teams

**GitHub Portfolio tips:**
- Pin 3–5 ML projects on your GitHub profile
- Make sure each repo has a detailed README with results and how to run it
- Use tags to mark working versions (`v1.0`, `v2.0`)
- Never commit notebooks with raw cell output — clear them first

You are now equipped to manage ML projects like a professional. Every commit is a step in the story of your project — make it a story worth reading.
