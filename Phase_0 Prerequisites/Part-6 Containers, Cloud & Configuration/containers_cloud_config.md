# Phase 00 (MLOps Track), Part 6 — Containers, Cloud & Configuration Fundamentals

> **Who this is for:** You've done Part 1 (dev environment), Part 4 (APIs &
> the web), and Part 5 (the ML model lifecycle primer). This part covers
> the infrastructure layer almost every MLOps tool assumes you already
> understand: containers, the cloud, and YAML.  
> **A note on testing:** Docker itself cannot run inside the sandboxed
> environment I write and test this course in (it would require running a
> container inside a container, which sandboxed environments deliberately
> block). Every Python script and every YAML example in this guide **was**
> actually run and verified. The Docker commands follow long-established,
> extremely stable syntax I'm confident in, but I want to be upfront about
> that one boundary rather than imply I clicked through and watched it
> work, the way I have for everything else.  
> **Time:** 2-3 hours.

---

## Table of Contents

1. [Why This Part Matters](#1-why-this-part-matters)
2. [What Is a Container, Really?](#2-what-is-a-container-really)
3. [Docker — Hands-On From Zero](#3-docker--hands-on-from-zero)
4. [What Is "The Cloud," Really?](#4-what-is-the-cloud-really)
5. [Cloud Building Blocks: Compute & Storage](#5-cloud-building-blocks-compute--storage)
6. [YAML — The Format Almost Every MLOps Tool Speaks](#6-yaml--the-format-almost-every-mlops-tool-speaks)
7. [Putting It Together — The MLOps Infrastructure Skeleton](#7-putting-it-together--the-mlops-infrastructure-skeleton)
8. [Hands-On: Containerize Your First Model](#8-hands-on-containerize-your-first-model)
9. [Troubleshooting FAQ](#9-troubleshooting-faq)
10. [Key Takeaways](#10-key-takeaways)
11. [What's Next](#11-whats-next)

---

## 1. Why This Part Matters

Part 5 gave you the model lifecycle: collect data, train, evaluate,
deploy, monitor, repeat. This part gives you the **infrastructure that
lifecycle actually runs on**. Three pieces, and you'll see all three again
in literally every MLOps tool you ever touch:

- **Containers** — how a trained model and everything it needs to run gets
  packaged into something that behaves identically anywhere
- **The cloud** — where that container, and the data it needs, actually
  lives and runs, since "my laptop" stops being a reasonable answer the
  moment more than one person depends on a model staying up
- **YAML** — the format you'll use to configure nearly every piece of
  MLOps tooling you'll meet from here on (Docker Compose, Kubernetes,
  CI/CD pipelines, MLflow projects)

---

## 2. What Is a Container, Really?

### 2.1 The "it works on my machine" problem

A model that runs perfectly on a data scientist's laptop can fail the
moment it's moved anywhere else — a different Python version, a missing
system library, a different operating system entirely. Every one of these
mismatches has caused real, painful production incidents.

### 2.2 The shipping container analogy

This is genuinely where the name comes from. Before standardized shipping
containers existed, loading a ship meant manually handling thousands of
oddly-shaped crates, barrels, and sacks — slow, inconsistent, and every
port needed different equipment for different cargo. The shipping
container solved this with one idea: **put anything inside a
standardized box, and every crane, every ship, every truck in the world
can move it identically**, without ever needing to know what's inside.

```
Before containers:                  With containers:
┌──────────────────┐               ┌──────────────────┐
│ 1000 oddly shaped │               │  Standardized     │
│ crates, barrels,  │               │  boxes — any       │
│ sacks — every port │               │  crane, ship, or   │
│ needs different    │               │  truck handles      │
│ handling           │               │  them identically    │
└──────────────────┘               └──────────────────┘
```

A software container does exactly this for code: it packages your
script, the exact Python version it needs, every library it depends on,
and any system-level dependencies, into one standardized unit that runs
identically on your laptop, a teammate's machine, or a cloud server —
none of them need to know or care what's inside.

### 2.3 Containers vs virtual machines, briefly

You may have heard of **virtual machines (VMs)** too — they solve a
similar-sounding problem differently. A VM virtualizes an entire
computer, including its own full operating system, which makes it heavy
(gigabytes, minutes to start). A container shares the host machine's
underlying operating system and only packages the application and its
specific dependencies, making it dramatically lighter (megabytes, starts
in seconds). This is exactly why containers, not VMs, became the standard
unit of deployment for MLOps and most of modern software.

```
Virtual Machine                     Container
┌─────────────────┐                ┌─────────────────┐
│   Application     │                │   Application    │
├─────────────────┤                ├─────────────────┤
│  Full Guest OS     │                │  (shares host OS) │
├─────────────────┤                └─────────────────┘
│   Hypervisor        │                ┌─────────────────┐
├─────────────────┤                │   Host OS          │
│   Host OS            │                └─────────────────┘
└─────────────────┘
   heavy, slow to start                light, fast to start
```

### 2.4 Images vs containers — the distinction that trips everyone up

These two words get used almost interchangeably by beginners, and getting
them straight early saves a lot of confusion:

| Term | What it actually is | Analogy |
|---|---|---|
| **Image** | A static blueprint — the packaged files, dependencies, and instructions, sitting on disk, not running | A recipe, or a class definition (Phase 00 Part 6 of the AI Engineer track, if you've done it) |
| **Container** | A running instance of an image | A baked cake from that recipe, or an *object* created from that class |

You can create many running containers from the exact same image, just
like you can bake many cakes from one recipe, or create many objects from
one class.

---

## 3. Docker — Hands-On From Zero

**Docker** is the dominant tool for building and running containers.
"Containerizing" something just means packaging it as a Docker image.

### 3.1 Installing Docker Desktop

1. Go to **[docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)**
2. Download the installer for your OS (Windows or Mac)
3. Run it, accepting the default options
4. **Windows specifically:** Docker Desktop requires WSL2 (Windows
   Subsystem for Linux) — the installer will prompt you to enable this if
   it isn't already, and may ask you to restart your computer
5. Launch Docker Desktop — you'll see a whale icon appear in your system
   tray (Windows) or menu bar (Mac) once it's running

### 3.2 Verify it worked

Open your terminal (Part 1) and run:

```bash
docker --version
```

You should see something like `Docker version 27.x.x`. Then try:

```bash
docker run hello-world
```

This downloads a tiny test image and runs it. You should see a friendly
message starting with "Hello from Docker!" — confirming Docker can pull
images and run containers successfully.

### 3.3 Key vocabulary

| Term | Meaning |
|---|---|
| **Registry** | A server that stores and distributes images — Docker Hub is the default, public one |
| **Pull** | Downloading an image from a registry to your machine |
| **Push** | Uploading an image you built to a registry |
| **Tag** | A label identifying a specific version of an image, e.g. `python:3.11` |

When you ran `docker run hello-world`, Docker automatically **pulled**
the `hello-world` image from Docker Hub (the default **registry**), since
it didn't already exist on your machine.

### 3.4 Running something more useful

```bash
docker run -it python:3.11 python
```

This pulls an official Python image and drops you into a real Python
interpreter — **running entirely inside a container**, completely
isolated from whatever Python version (if any) is installed on your
actual machine. Try typing `print("hello from inside a container")` and
pressing Enter. Type `exit()` to leave.

The `-it` flag makes the session interactive (`-i`) and gives you a
proper terminal connection (`-t`) — you'll use this combination constantly.

### 3.5 Basic commands you'll use constantly

| Command | What it does |
|---|---|
| `docker images` | List images you've downloaded or built |
| `docker ps` | List currently running containers |
| `docker ps -a` | List all containers, including stopped ones |
| `docker stop <container>` | Stop a running container |
| `docker rm <container>` | Delete a stopped container |
| `docker rmi <image>` | Delete an image |

### 3.6 Writing your first Dockerfile

A **Dockerfile** is a plain text file containing instructions for
building an image — the "recipe" from Section 2.4's analogy. Section 8
walks through a complete, real example; here's the shape first:

```dockerfile
FROM python:3.11-slim      # start from an existing image as the base
WORKDIR /app                # set the working directory inside the container
COPY requirements.txt .     # copy a file from your machine into the image
RUN pip install -r requirements.txt   # run a command WHILE BUILDING the image
COPY . .                    # copy the rest of your code in
CMD ["python", "app.py"]    # the command that runs when a container STARTS
```

Each line builds on the line before it, creating the final image
step by step. `RUN` happens once, while building the image. `CMD` happens
every time someone starts a new container from that image.

---

## 4. What Is "The Cloud," Really?

### 4.1 The honest, no-marketing definition

**"The cloud" is just someone else's computer, sitting in a data center
somewhere, that you rent access to over the internet** — instead of
buying, owning, and maintaining physical hardware yourself.

```
Before cloud computing:              With cloud computing:
You buy a physical server             You rent computing power
(expensive, you maintain it,           from a provider (AWS, GCP, Azure),
fixed capacity, sits idle              pay only for what you use,
sometimes)                             scale up or down on demand
```

### 4.2 Why MLOps lives in the cloud

Training a model can demand far more compute than a laptop has — and only
for the duration of training, not constantly. Serving a model in
production needs to stay reliably available, with capacity that scales
with demand. Renting exactly the capacity you need, exactly when you need
it, is a far better economic fit for this pattern than owning fixed
hardware that's sometimes idle and sometimes not enough.

### 4.3 The major providers

You don't need to be an expert in any of these yet — just recognize the
names, since MLOps job postings and tooling reference them constantly:

| Provider | Short name |
|---|---|
| Amazon Web Services | AWS |
| Google Cloud Platform | GCP |
| Microsoft Azure | Azure |

Each offers broadly equivalent core services (Section 5) under different
names — the underlying concepts transfer between all three.

---

## 5. Cloud Building Blocks: Compute & Storage

### 5.1 Compute — a rented computer

The most basic cloud service is **compute** — a virtual machine (Section
2.3) you rent, that you can connect to remotely and use almost exactly
like your own computer, except it lives in the provider's data center and
you pay for the time you use it.

```
Your laptop  ──── SSH connection ────►  A rented cloud VM
(client)          (remote login,          (running somewhere
                   like a very long-       in a data center,
                   distance terminal       doing the actual
                   session)                 work)
```

**SSH** (Secure Shell) is the standard way to remotely log into and
control another computer's terminal over the internet — this is exactly
how you'd connect to a cloud VM to run training jobs or manage a server.

### 5.2 Storage — a place for files that isn't tied to one computer

**Object storage** (AWS calls it S3, GCP calls it Cloud Storage, Azure
calls it Blob Storage) is a place to put files — datasets, **model
artifacts** (Part 5, Section 8!) — that lives independently of any single
computer, reliably accessible from anywhere, by anything with permission.

This is exactly where the model lifecycle's "store the artifact somewhere
reliable" requirement (Part 5, Section 8.2) gets solved in practice: a
trained model gets saved, uploaded to object storage, and from there can
be pulled down by whatever serving infrastructure needs to load it —
completely decoupled from whichever machine happened to train it.

### 5.3 Managed ML platforms, briefly

All three major providers also offer higher-level, ML-specific platforms
built on top of their core compute and storage — AWS SageMaker, GCP
Vertex AI, Azure ML. These bundle together training infrastructure,
experiment tracking, model registries, and deployment tooling into one
service. You'll work with these properly in the MLOps phases ahead — for
now, just know they exist as a layer above the raw compute/storage
building blocks this section covers.

### 5.4 How this connects back to Docker

A typical real pattern: you build a Docker image (Section 3) containing
your trained model and the code to serve predictions from it, push that
image to a registry, and then run it on cloud compute (Section 5.1) —
the exact same image runs identically whether you test it on your laptop
or deploy it to a server with a thousand times the traffic. This is the
entire reason Sections 3 and 5 are taught together: **containers are what
you deploy, the cloud is where you deploy them.**

---

## 6. YAML — The Format Almost Every MLOps Tool Speaks

### 6.1 What YAML is, and why it exists alongside JSON

You already know JSON (Part 4) — a text format for structured data. YAML
("YAML Ain't Markup Language") represents the **exact same kinds of
data** — objects, lists, key-value pairs — but is designed to be easier
for **humans** to read and write by hand, which is exactly why almost
every tool whose config files are meant to be hand-edited (Docker
Compose, Kubernetes, CI/CD pipelines) uses YAML instead of JSON.

### 6.2 YAML syntax basics

```yaml
# This is a comment — JSON cannot do this, YAML can
name: my-model-service
version: 1.0
debug: false

# Nesting is done with indentation, not curly braces
database:
  host: localhost
  port: 5432

# Lists use a dash
dependencies:
  - scikit-learn
  - joblib
  - numpy
```

| YAML syntax | Meaning |
|---|---|
| `key: value` | A key-value pair (no quotes needed for simple strings) |
| Indentation | Defines nesting — like JSON's `{ }`, but using whitespace instead |
| `- item` | A list entry (like JSON's `[ ]`) |
| `#` | A comment — ignored when the file is read |

### 6.3 YAML vs JSON, side by side

The exact same data, in both formats:

```yaml
# YAML
name: Claude
is_helpful: true
skills:
  - writing
  - coding
creator:
  company: Anthropic
```

```json
{
  "name": "Claude",
  "is_helpful": true,
  "skills": ["writing", "coding"],
  "creator": {
    "company": "Anthropic"
  }
}
```

Same structure, same data — YAML just drops the brackets and quotes in
favor of indentation, and adds comment support.

### 6.4 Common YAML gotchas

**Indentation must be spaces, not tabs.** Most YAML parsers reject tabs
outright, and inconsistent indentation is the single most common YAML
error beginners hit.

**Indentation level matters precisely** — two keys at the same logical
level must be indented by exactly the same amount. Most editors (VS Code
included) auto-detect this for `.yaml`/`.yml` files and help you stay
consistent.

**You've already used YAML without necessarily noticing** — Phase 08 of
the AI Engineer track's `docker-compose.yml` is written in exactly this
format.

### 6.5 Hands-on: reading YAML in Python

```bash
pip install pyyaml
```

```python
import yaml

config_text = """
name: my-model-service
version: 1.0
dependencies:
  - scikit-learn
  - joblib
"""

config = yaml.safe_load(config_text)

print(config["name"])           # → my-model-service
print(config["dependencies"])   # → ['scikit-learn', 'joblib']
print(type(config))             # → <class 'dict'>
```

Exactly like `json.loads()` converts JSON text into a Python dictionary
(Part 4), `yaml.safe_load()` does the same for YAML — confirming YAML and
JSON really are just two different spellings of the same underlying idea.

---

## 7. Putting It Together — The MLOps Infrastructure Skeleton

```
  Your code + trained model artifact (Part 5)
                  │
                  ▼
       Packaged into a Docker IMAGE (Section 2.4)
       using instructions in a Dockerfile (Section 3.6)
                  │
                  ▼
       Configuration describing how to run it,
       written in YAML (Section 6)
                  │
                  ▼
       Deployed as a running CONTAINER (Section 2.4)
       on rented CLOUD COMPUTE (Section 5.1)
                  │
                  ▼
       Reading/writing data and artifacts from
       CLOUD STORAGE (Section 5.2)
```

This is, at its core, the shape of nearly every real MLOps deployment
you'll encounter — the specific tools change (Kubernetes instead of plain
Docker, a managed platform instead of raw cloud compute), but this
skeleton — containerize, configure, deploy, store — stays the same.

---

## 8. Hands-On: Containerize Your First Model

Let's bring Part 5's model training together with this part's container
skills. You'll train a tiny model, save it as an artifact, write a script
that loads and uses it, and package the whole thing as a Docker image.

### 8.1 Project setup

```bash
mkdir model-container-demo
cd model-container-demo
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install scikit-learn joblib numpy
```

### 8.2 Train and save a model

Create `train_model.py`:

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib

X, y = make_classification(
    n_samples=300, n_features=15, n_informative=4, n_redundant=2,
    n_classes=2, class_sep=1.2, flip_y=0.10, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Test accuracy: {accuracy:.1%}")

joblib.dump(model, "model.joblib")   # this is the model ARTIFACT (Part 5)
print("Model saved to model.joblib")
```

Run it:

```bash
python train_model.py
```

**Verified output:**
```
Test accuracy: 81.1%
Model saved to model.joblib
```

A new file, `model.joblib`, now sits in your folder — the actual trained
model, serialized to disk, ready to be loaded anywhere.

### 8.3 Write a script that uses the saved model

Create `predict.py` — this is the script we'll containerize:

```python
import joblib
import numpy as np

model = joblib.load("model.joblib")

# A single example input, in the same shape the model was trained on
sample = np.array([[0.5, -1.2, 0.3, 1.1, -0.4, 0.8, -0.6, 0.2,
                     1.4, -0.9, 0.1, -0.3, 0.7, -1.0, 0.4]])

prediction = model.predict(sample)
probability = model.predict_proba(sample)

print(f"Prediction: class {prediction[0]}")
print(f"Confidence: {probability[0][prediction[0]]:.1%}")
```

Run it directly first, to confirm it works before containerizing:

```bash
python predict.py
```

**Verified output:**
```
Prediction: class 1
Confidence: 93.8%
```

### 8.4 Write the requirements file

Create `requirements.txt`:

```
scikit-learn
joblib
numpy
```

### 8.5 Write the Dockerfile

Create a file named exactly `Dockerfile` (no extension):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model.joblib .
COPY predict.py .

CMD ["python", "predict.py"]
```

Walking through it line by line:
- `FROM python:3.11-slim` — start from an official, lightweight Python image
- `WORKDIR /app` — everything from here happens inside a folder called
  `/app` *inside* the container
- `COPY requirements.txt .` then `RUN pip install ...` — install
  dependencies first (Docker caches this layer, so rebuilding after only
  changing your code later won't reinstall everything from scratch)
- `COPY model.joblib .` and `COPY predict.py .` — bring in the trained
  artifact and the script that uses it
- `CMD [...]` — what runs automatically when someone starts a container
  from this image

### 8.6 Build and run it

```bash
docker build -t model-demo .
```

This reads your Dockerfile and builds an image named `model-demo`. You'll
see Docker step through each instruction in the Dockerfile in order.

```bash
docker run model-demo
```

**Expected output** (matching Section 8.3 exactly, since it's the same
code — just now running inside an isolated container instead of directly
on your machine):
```
Prediction: class 1
Confidence: 93.8%
```

**What you just did:** trained a model, saved it as an artifact, and
packaged both the artifact and the code that uses it into a single,
portable image that will produce this exact same output on any machine
with Docker installed — your laptop, a teammate's machine, or a cloud
server — without any of them needing Python, scikit-learn, or anything
else installed directly. **That portability is the entire point.**

---

## 9. Troubleshooting FAQ

**`docker: command not found`**
Docker Desktop isn't installed, isn't running, or didn't add itself to
your PATH. Confirm Docker Desktop is actually open (look for the whale
icon), and reinstall if `docker --version` still fails afterward.

**Windows: Docker Desktop asks about WSL2 and won't start**
Follow the prompt to install/enable WSL2 — Docker Desktop on Windows
requires it. This may require an admin-level terminal and a restart.

**`docker build` fails with a "file not found" error**
Make sure you're running the command from inside the folder containing
your Dockerfile, and that every file referenced in a `COPY` line (like
`model.joblib`) actually exists in that folder first — run
`train_model.py` before `docker build`, not after.

**My YAML file won't parse — "mapping values are not allowed" or similar**
Almost always an indentation problem: mixed tabs and spaces, or two keys
at the same level indented inconsistently. Check whitespace carefully —
this error is extremely common and not a sign anything is wrong with you.

**`docker run` succeeds but I don't see any output**
Some Docker setups buffer Python's output — add `-u` to force unbuffered
output: change the Dockerfile's last line to
`CMD ["python", "-u", "predict.py"]`.

---

## 10. Key Takeaways

1. **A container packages code with everything it needs to run, so it
   behaves identically anywhere** — solving "it works on my machine" the
   same way standardized shipping containers solved inconsistent cargo
   handling.

2. **An image is the static blueprint; a container is a running instance
   of it** — the same relationship as a class and an object.

3. **The cloud is rented compute and storage**, not a fundamentally
   different kind of computer — paying for capacity on demand instead of
   owning fixed hardware.

4. **Compute (VMs) is where things run; object storage is where files —
   including model artifacts — live**, independent of any single machine.

5. **YAML represents the same data JSON does, optimized for humans to
   hand-edit** — indentation instead of brackets, comments allowed, no
   required quotes for simple strings.

6. **The MLOps infrastructure skeleton — containerize, configure with
   YAML, deploy to cloud compute, store artifacts in cloud storage — is
   the shape behind nearly every real deployment** you'll encounter, no
   matter which specific tools sit on top of it.

7. **You containerized a real trained model in this guide** — that exact
   pattern (train → save artifact → write a serving script → Dockerfile →
   build → run) is the literal foundation of model deployment in
   production MLOps systems.

---

## 11. What's Next

You now have the full Phase 00 foundation for MLOps: dev environment and
Git (Part 1), Python fundamentals (Parts 2-3, shared with the AI Engineer
track), HTTP/APIs (Part 4, also shared), the model lifecycle (Part 5,
MLOps-specific), and now containers, cloud, and YAML (this part).

From here, the MLOps-specific phases ahead will go deep on: experiment
tracking with MLflow, building automated training pipelines, model
registries and versioning, CI/CD for ML, container orchestration with
Kubernetes, and production monitoring for drift — each phase building
directly on the vocabulary and hands-on skills from this entire Phase 00
series.
