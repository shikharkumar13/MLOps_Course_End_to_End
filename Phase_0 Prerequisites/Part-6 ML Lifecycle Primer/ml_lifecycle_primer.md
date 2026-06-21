# Phase 00 (MLOps Track), Part 5 — The ML Model Lifecycle Primer

> **Who this is for:** You're heading into an MLOps course, not an LLM/AI
> engineering one — this guide assumes nothing about machine learning, and
> covers the general model lifecycle (training, evaluating, deploying,
> monitoring) rather than LLM-specific concepts.  
> **Not what you want?** If you're on the AI Engineer track instead (LLM
> APIs, RAG, agents), use **Phase 00 Part 5 — A Gentle, No-Math AI Primer**
> instead of this one — that one covers tokens, embeddings, and how LLMs
> generate text, which this guide does not.  
> **What you'll have by the end:** A real understanding of what a "model"
> actually is, the full lifecycle MLOps exists to manage, and the
> vocabulary — train/test splits, overfitting, model artifacts, drift,
> experiment tracking — every MLOps tool you'll touch next assumes you
> already know.  
> **Time:** 1-2 hours.

---

## Table of Contents

1. [Why This Part Matters](#1-why-this-part-matters)
2. [What Is a Model, Really?](#2-what-is-a-model-really)
3. [Three Kinds of ML Problems](#3-three-kinds-of-ml-problems)
4. [The ML Lifecycle — The Whole Reason MLOps Exists](#4-the-ml-lifecycle--the-whole-reason-mlops-exists)
5. [Train, Validation & Test Splits](#5-train-validation--test-splits)
6. [Overfitting & Underfitting](#6-overfitting--underfitting)
7. [Evaluation Metrics, Gently](#7-evaluation-metrics-gently)
8. [What Is a Model Artifact?](#8-what-is-a-model-artifact)
9. [Experiment Tracking — Why You Need It](#9-experiment-tracking--why-you-need-it)
10. [Model & Data Drift](#10-model--data-drift)
11. [Where Deep Learning & LLMs Fit In](#11-where-deep-learning--llms-fit-in)
12. [Hands-On: Train Your First Model, and Watch It Overfit](#12-hands-on-train-your-first-model-and-watch-it-overfit)
13. [What This Primer Is — and Isn't](#13-what-this-primer-is--and-isnt)
14. [Key Takeaways](#14-key-takeaways)
15. [What's Next](#15-whats-next)

---

## 1. Why This Part Matters

MLOps tooling — MLflow, model registries, CI/CD for ML, monitoring
dashboards — is built entirely around managing a process: a model gets
trained, evaluated, deployed, and watched over time. If you don't have a
clear mental model of *what that process actually is*, every MLOps tool
you learn will feel like memorizing button-clicks instead of understanding
why the tool exists.

This guide builds that mental model first, with zero math — by the end,
words like "overfitting," "model artifact," "drift," and "experiment
tracking" will be concepts you understand, not jargon you've memorized.

---

## 2. What Is a Model, Really?

### 2.1 The plain definition

A **model** is a function — something that takes an input and produces an
output — except instead of a human writing the exact logic, the model
*learned* that logic from examples (this is the same "learning from
examples instead of hand-written rules" idea at the heart of all machine
learning).

```
Traditional function (human-written):
   def is_adult(age):
       return age >= 18

ML model (learned from examples):
   model.predict(house_features) → predicted_price
   (nobody wrote the pricing formula by hand — the model learned
    the relationship between features and price from thousands of
    real examples of houses and their actual sale prices)
```

### 2.2 The "function" framing matters for MLOps specifically

Thinking of a model as "a function that was learned, not written" explains
why MLOps is its own discipline, separate from regular software
engineering. A normal function, once written and tested, doesn't change —
deploy it once and it behaves identically forever. A model's "logic" was
learned from a specific snapshot of data — and the real world keeps
changing after that snapshot was taken. That mismatch, growing over time,
is the central problem MLOps exists to manage (see Section 10).

---

## 3. Three Kinds of ML Problems

You'll see these terms constantly, so a quick map:

| Type | What it predicts | Example |
|---|---|---|
| **Classification** | One of a fixed set of categories | "Is this email spam or not spam?" |
| **Regression** | A continuous number | "What will this house sell for?" |
| **Clustering** | Groupings, with no predefined categories | "Group these customers into similar segments" |

Classification and regression are both examples of **supervised
learning** — the model learns from labeled examples (you already know the
right answer for each training example, like Section 2's spam emails
labeled spam/not-spam). Clustering is **unsupervised learning** — there
are no labels; the model finds structure on its own.

This course's hands-on exercise (Section 12) is a classification problem
— you'll see exactly how this plays out in real code.

---

## 4. The ML Lifecycle — The Whole Reason MLOps Exists

This is the single most important diagram in this entire guide. Every
MLOps tool you'll ever use exists to support one or more stages of this
loop:

```
   ┌─────────────┐
   │ 1. Collect & │
   │    prepare    │
   │    data       │
   └──────┬───────┘
          ▼
   ┌─────────────┐
   │ 2. Train a    │
   │    model      │
   └──────┬───────┘
          ▼
   ┌─────────────┐
   │ 3. Evaluate   │──── not good enough? ──┐
   │    it         │                         │
   └──────┬───────┘                         │
          │ good enough                      │
          ▼                                  │
   ┌─────────────┐                          │
   │ 4. Deploy it  │                          │
   │    to         │                          │
   │    production │                          │
   └──────┬───────┘                          │
          ▼                                  │
   ┌─────────────┐                          │
   │ 5. Monitor    │──── performance drops ──┘
   │    it in       │     (drift, Section 10)
   │    production   │
   └─────────────┘
```

A regular software project mostly lives in steps that look like "write
code, test it, ship it" — once. **An ML project never really leaves this
loop.** A model that performed great at launch can quietly get worse over
time as the real world drifts away from the data it was trained on,
forcing you back to step 1 with fresh data, again and again.

**MLOps is the discipline of making this entire loop reliable, repeatable,
and observable — instead of a one-off manual process a single data
scientist remembers how to do.**

---

## 5. Train, Validation & Test Splits

### 5.1 Why one dataset isn't enough

A natural instinct is to train your model on all the data you have, then
check how well it does — on that same data. This is a trap: a model can
simply **memorize** the exact examples it was trained on, scoring
perfectly, while having learned nothing that generalizes to new, unseen
data. You'd think you have a great model and be completely wrong.

### 5.2 The exam-studying analogy

```
Training set    →  Your textbook and homework problems
                    (the model studies these directly)

Validation set  →  Practice exams
                    (used WHILE preparing, to tune your approach —
                     in ML, this is used to tune settings called
                     "hyperparameters" without touching the real test)

Test set        →  The actual final exam
                    (touched only ONCE, at the very end, to get an
                     honest, unbiased measure of how well you actually learned)
```

A model is trained only on the **training set**. While experimenting with
different settings, you check progress against the **validation set** —
never the test set, because repeatedly peeking at the test set and
adjusting based on it is exactly like seeing the final exam questions
early; your "honest" final score stops being honest. Only at the very end,
once you've settled on a final model, do you check performance on the
**test set** — exactly once, as the true, unbiased measure of how it'll
likely perform on real, never-seen-before data.

### 5.3 Typical split

A common starting point: 70% training, 15% validation, 15% test — though
exact ratios vary by project and dataset size. The principle matters far
more than the exact percentages: **never let the test set influence any
decision before the final evaluation.**

---

## 6. Overfitting & Underfitting

### 6.1 Overfitting — memorizing instead of learning

**Overfitting** is what happens when a model learns the training data *too
specifically* — including its noise and quirks — instead of learning the
general pattern underneath. An overfit model scores excellently on
training data and noticeably worse on new data, because it memorized
specific examples rather than learning a rule that generalizes.

```
Training accuracy:    99%   ← suspiciously high
Test accuracy:         71%   ← the real story: it didn't generalize well
                ↑
       big gap = overfitting
```

### 6.2 Underfitting — not learning enough

**Underfitting** is the opposite problem: the model is too simple to
capture the real pattern in the data at all, and performs poorly on
*both* training and test data.

```
Training accuracy:    65%   ← bad even on data it trained on
Test accuracy:          63%   ← consistently bad — underfitting
```

### 6.3 The target: generalization

The goal is a model whose training and test performance are both strong
*and close together* — evidence it learned a genuine, generalizable
pattern rather than memorizing specifics or failing to learn at all.

```
Training accuracy:     91%
Test accuracy:           89%   ← small gap, both strong = good generalization
```

You'll see this exact phenomenon for real in Section 12's hands-on exercise.

---

## 7. Evaluation Metrics, Gently

You don't need formulas memorized — just the intuition for what each
metric is actually asking.

| Metric | The question it answers |
|---|---|
| **Accuracy** | "Out of everything, what fraction did the model get right?" |
| **Precision** | "When the model said 'yes,' how often was it actually right?" |
| **Recall** | "Out of everything that was actually a 'yes,' how many did the model catch?" |
</br>

**Why accuracy alone can be misleading:** imagine a model detecting a rare
disease that affects 1 in 1,000 people. A model that *always* predicts
"no disease" would be 99.9% accurate — and completely useless, since it
never catches a single real case. This is exactly why precision and
recall exist alongside accuracy: they reveal a model's behavior on the
cases that actually matter, which a single accuracy number can hide.

A **confusion matrix** is simply a small table laying out exactly how
many predictions fell into each of four buckets: correctly predicted
yes, correctly predicted no, incorrectly predicted yes (a "false
positive"), and incorrectly predicted no (a "false negative") — precision
and recall are both just different ways of summarizing this same table.

---

## 8. What Is a Model Artifact?

### 8.1 The definition

Once a model finishes training, its learned internal settings (Phase 00's
AI-track Part 5 calls these "dials," and you'll see the formal term
**parameters** or **weights** used the same way here) get saved to a file
— this saved file is called a **model artifact**.

```
Training process (uses lots of data, takes time)
            │
            ▼
    model.pkl  /  model.pt  /  model.onnx   ← the model artifact
            │      (the actual file you deploy)
            ▼
   Loaded into a serving application,
   ready to make predictions on new data
```

### 8.2 Why this matters for MLOps specifically

Once you understand a model artifact is just a file, several MLOps
practices become obvious:

- **Versioning** — like any important file, you want to track changes to
  it over time, know exactly which artifact is currently in production,
  and be able to roll back to a previous one if a new one performs worse
- **Storage** — artifacts need to live somewhere reliable, accessible to
  whatever system serves predictions — this is exactly what a **model
  registry** (a tool you'll meet properly in the MLOps phases) manages
- **Reproducibility** — given the same training data and settings, can you
  regenerate the exact same artifact? This question is central to trusting
  an ML pipeline

---

## 9. Experiment Tracking — Why You Need It

### 9.1 The problem

Training a good model is rarely a single attempt — it's dozens or
hundreds of attempts, each with slightly different data, settings, or
approaches. Without a system for it, you very quickly lose track of which
attempt used which data, which settings produced which result, and which
saved file corresponds to which attempt.

```
attempt_47_final_v2_USE_THIS_ONE.pkl
attempt_47_final_v2_ACTUALLY_USE_THIS.pkl
attempt_52_better_maybe.pkl
```

This is a genuinely common, painful failure mode without proper tooling.

### 9.2 What experiment tracking solves

**Experiment tracking** tools (you'll work hands-on with MLflow or
similar in the MLOps phases) automatically record, for every training
run: what data was used, what settings were chosen, what the resulting
metrics were, and where the resulting artifact is stored — all
searchable, comparable, and reproducible later, instead of living in
filenames and someone's memory.

---

## 10. Model & Data Drift

### 10.1 Why a deployed model can quietly get worse

Recall Section 2.2: a model's logic was learned from a specific snapshot
of data. The real world doesn't stay still. Two related problems emerge
over time:

**Data drift** — the *inputs* the model sees in production start looking
statistically different from the data it was trained on. Example: a model
trained on pre-pandemic shopping behavior, now seeing radically different
purchasing patterns.

**Model drift** (also called concept drift) — the actual *relationship*
between inputs and the correct output changes. Example: the features that
predicted "good loan applicant" before an economic shift no longer predict
the same outcome afterward.

```
Day 1 (launch):       Model accuracy: 94%   ✓ great
Month 3:               Model accuracy: 89%   slightly worse
Month 8:                Model accuracy: 71%   the world has moved on —
                                                this model needs retraining
```

### 10.2 Why this is the core argument for MLOps as a discipline

This is precisely why "deploy it and walk away" doesn't work for ML
systems the way it often can for regular software. **Monitoring deployed
models for drift, and having a reliable process to retrain and redeploy
when needed, is a primary reason MLOps exists as a distinct discipline**
— not a one-time deployment task, but an ongoing operational
responsibility.

---

## 11. Where Deep Learning & LLMs Fit In

Everything in this guide applies whether your model is a simple decision
tree or a billion-parameter neural network — the lifecycle (Section 4),
the train/test discipline (Section 5), overfitting (Section 6), artifacts
(Section 8), and drift (Section 10) are universal.

**Deep learning** (neural networks with many layers, Phase 00's AI-track
Part 5 covers this in depth) is one *family* of models within this same
lifecycle — a particularly powerful one, especially for unstructured data
like images and text, but operationally it's managed the same way: train,
evaluate, deploy, monitor.

**LLMs** are a specific, very large-scale application of deep learning,
trained for one core skill (predicting the next piece of text). If your
MLOps work eventually involves deploying and monitoring LLM-based
systems specifically, the AI Engineer track's Phase 00 Part 5 (and
Phases 01-08 generally) covers that territory in depth — this guide gave
you the general MLOps foundation that applies regardless of model type.

---

## 12. Hands-On: Train Your First Model, and Watch It Overfit

Time to make Sections 5 and 6 concrete. We'll use **scikit-learn**, the
standard, lightweight library for classical ML in Python — no GPU needed,
installs in seconds, and includes small practice datasets built in (no
downloads, no API keys).

### 12.1 Setup

```bash
pip install scikit-learn
```

### 12.2 The dataset

We'll generate a **synthetic dataset** using scikit-learn's
`make_classification` — 300 examples, each with 15 numeric features, and
a label (one of two classes) to predict. This is a **classification
problem** (Section 3). Crucially, we'll deliberately add some label noise
(10% of labels randomly flipped) to mimic how messy real-world data
actually is — a perfectly clean toy dataset (like the classic Iris
flowers dataset) is often *too easy*, and an unrestricted model can
achieve 100% on both training and test data, which would hide the exact
phenomenon this exercise wants you to see.

### 12.3 The code

Create a file called `train_and_overfit.py`:

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# A synthetic classification dataset, tuned to have a real, learnable
# pattern PLUS enough noise that an overly complex model can memorize
# spurious detail instead of the true pattern — this is what makes the
# overfitting demonstration below actually visible (a perfectly clean
# dataset like Iris is too easy for this to show up).
X, y = make_classification(
    n_samples=300,
    n_features=15,
    n_informative=4,
    n_redundant=2,
    n_classes=2,
    class_sep=1.2,
    flip_y=0.10,        # 10% randomly mislabeled — real-world-style noise
    random_state=42,
)

# Section 5: split into training data and test data.
# random_state=42 just makes the split reproducible every time you run this.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

print(f"Training examples: {len(X_train)}")
print(f"Test examples:     {len(X_test)}")


def train_and_evaluate(max_depth, label):
    """
    Train a decision tree and report both training and test accuracy.
    max_depth controls how complex the tree is allowed to become —
    None means "no limit," which is exactly how we'll demonstrate
    overfitting below.
    """
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)   # this is "training" — the model learns

    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)

    train_accuracy = accuracy_score(y_train, train_predictions)
    test_accuracy = accuracy_score(y_test, test_predictions)

    gap = train_accuracy - test_accuracy

    print(f"\n{label}")
    print(f"  Training accuracy: {train_accuracy:.1%}")
    print(f"  Test accuracy:     {test_accuracy:.1%}")
    print(f"  Gap:               {gap:.1%}  "
          f"{'<- overfitting!' if gap > 0.08 else '<- good generalization'}")


print("\n" + "=" * 50)
print("Comparing model complexity")
print("=" * 50)

train_and_evaluate(max_depth=3,    label="Simple model (max_depth=3)")
train_and_evaluate(max_depth=None, label="Unrestricted model (max_depth=None)")
```

### 12.4 Run it

```bash
python train_and_overfit.py     # Windows
python3 train_and_overfit.py    # Mac
```

### 12.5 What you should see

```
Simple model (max_depth=3)
  Training accuracy: 87.1%
  Test accuracy:     81.1%
  Gap:               6.0%   <- good generalization

Unrestricted model (max_depth=None)
  Training accuracy: 100.0%
  Test accuracy:     81.1%
  Gap:               18.9%  <- overfitting!
```

The simple, depth-limited model shows training and test accuracy
reasonably close together — good generalization, exactly as Section 6.3
described. The unrestricted model memorizes the training data **perfectly**
(100%) — but gets **no better** on the test set than the simple model did.
**That's the overfitting signature: more complexity bought zero real
improvement, it just memorized noise.** That gap is happening in front of
you, with a real model you just trained.

Try changing `max_depth` to other values (4, 6, 10) and re-running — watch
how the gap changes as the model is allowed to become more or less
complex. This single, tunable number is exactly the kind of setting
**experiment tracking** (Section 9) exists to record across many training
attempts.

---

## 13. What This Primer Is — and Isn't

**This primer genuinely is enough** to start MLOps-focused phases without
core vocabulary feeling unexplained — the lifecycle, train/test
discipline, overfitting, artifacts, drift, and experiment tracking are
the concepts every MLOps tool assumes you already have a feel for.

**What's intentionally left out:** the actual mathematics of how a model
learns (gradient descent, loss functions), the internals of specific
algorithms (how a decision tree actually picks its splits, how a neural
network's layers are structured), and statistical theory behind why
certain metrics behave the way they do. None of that is required to
understand *what MLOps manages* — only to build models from scratch
yourself, which is a data scientist's job, not strictly an MLOps
engineer's.

---

## 14. Key Takeaways

1. **A model is a learned function, not a hand-written one** — and because
   it was learned from a specific data snapshot, it can go stale as the
   real world changes. That single fact is the root reason MLOps exists.

2. **The ML lifecycle — collect data, train, evaluate, deploy, monitor,
   repeat — is the organizing structure behind every MLOps tool** you'll
   encounter. Each tool exists to make one or more stages of this loop
   reliable and repeatable.

3. **Train/validation/test splits exist to give you an honest measure of
   generalization** — never let the test set influence decisions before
   the final evaluation, or your "honest" score stops being honest.

4. **Overfitting is memorizing instead of learning** — visible as a gap
   between training and test performance. You just watched this happen
   in real code in Section 12.

5. **A model artifact is just a saved file** — versioning, storing, and
   reliably deploying that file is a huge part of what MLOps tooling
   (model registries, deployment pipelines) actually does.

6. **Experiment tracking exists because "which file was my best model
   again?" is a real, common, painful problem** without it.

7. **Drift is why deployment isn't the finish line** — a model's
   performance can quietly degrade as the world changes, which is why
   monitoring and retraining are ongoing MLOps responsibilities, not a
   one-time task.

---

## 15. What's Next

You now have the general ML vocabulary every MLOps tool assumes — the
lifecycle, train/test discipline, overfitting, artifacts, drift, and
experiment tracking.

**Part 6 (MLOps Track) — Containers, Cloud & Configuration Fundamentals**
comes next: what Docker and containers actually are and why MLOps relies
on them from day one, what "the cloud" concretely means (VMs, storage),
and how to read and write YAML — the format almost every MLOps tool
configures itself with.

Say **"Start MLOps Part 6"** when you're ready.
