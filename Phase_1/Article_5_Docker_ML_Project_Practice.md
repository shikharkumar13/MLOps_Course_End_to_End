# Article 5: Docker in Action — Dockerizing a Real ML Project

*A complete hands-on walkthrough: containerizing a Heart Disease prediction API, with every line of the Dockerfile explained in plain words*

---

## Introduction

In Article 4 you learned what Docker is, how it works, and how to write a Dockerfile. Now we put it all into practice. We'll take a small, working machine learning project — a Heart Disease prediction service — and containerize it from start to finish.

By the end of this article you will have:
- A real ML project packaged into a Docker image
- A Dockerfile where you understand **every single line**
- A running container serving predictions through an API
- The confidence to Dockerize your own ML projects

We'll go slowly and explain everything, because the goal is understanding, not just copying commands.

---

## Part 1 — The Project We're Containerizing

We'll build a simple ML service that predicts whether a patient has heart disease based on their health measurements. It has two parts:

1. **A training script** that trains a model and saves it.
2. **A prediction API** (using Flask) that loads the saved model and serves predictions over HTTP.

### Project Structure

```
heart_disease_docker/
├── Dockerfile              ← the recipe (we'll write this)
├── .dockerignore           ← files to exclude from the image
├── requirements.txt        ← Python dependencies
├── train.py                ← trains and saves the model
├── app.py                  ← Flask API that serves predictions
├── data/
│   └── heart.csv           ← the dataset
└── models/
    └── model.pkl           ← the trained model (created by train.py)
```

Let's create the project files first, then write the Dockerfile.

---

## Part 2 — Building the ML Project (Before Docker)

### Step 2.1 — The Requirements File

**`requirements.txt`** lists the exact Python packages and versions our project needs:

```
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.4
joblib==1.3.2
flask==3.0.0
```

> Pinning exact versions (with `==`) is essential for reproducibility — it guarantees the container installs the same versions every time.

### Step 2.2 — The Training Script

**`train.py`** loads the data, trains a Random Forest, and saves the model:

```python
"""train.py — Train a heart disease classifier and save it."""
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the data
df = pd.read_csv("data/heart.csv")

# Split into features (X) and target (y)
X = df.drop(columns=["target"])
y = df["target"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train the model
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Evaluate
accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Model trained. Test accuracy: {accuracy:.4f}")

# Save the model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.pkl")
print("Model saved to models/model.pkl")
```

### Step 2.3 — The Prediction API

**`app.py`** is a Flask web server that loads the model and returns predictions:

```python
"""app.py — Flask API serving heart disease predictions."""
from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Load the trained model once when the app starts
model = joblib.load("models/model.pkl")

# The 13 feature names the model expects
FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]


@app.route("/health", methods=["GET"])
def health():
    """Simple health check to confirm the API is running."""
    return jsonify({"status": "healthy"})


@app.route("/predict", methods=["POST"])
def predict():
    """Accept patient data as JSON and return a prediction."""
    data = request.get_json()

    # Build a DataFrame from the input in the correct feature order
    input_df = pd.DataFrame([[data[f] for f in FEATURES]], columns=FEATURES)

    # Make a prediction
    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])

    return jsonify({
        "prediction": prediction,           # 1 = disease, 0 = no disease
        "probability": round(probability, 4),
        "interpretation": "Heart disease likely" if prediction == 1
                          else "Heart disease unlikely"
    })


if __name__ == "__main__":
    # host="0.0.0.0" makes the app reachable from OUTSIDE the container
    app.run(host="0.0.0.0", port=5000)
```

> **Critical detail:** `host="0.0.0.0"` is essential inside Docker. If you use the default `127.0.0.1`, the app would only be reachable from *inside* the container and you couldn't access it from your laptop. We'll revisit this.

### Step 2.4 — The .dockerignore File

**`.dockerignore`** tells Docker what NOT to copy into the image, keeping it lean:

```dockerignore
# Python cache
__pycache__/
*.pyc
*.pyo

# Virtual environments
.venv/
venv/

# Git
.git/
.gitignore

# Jupyter
.ipynb_checkpoints/

# Docs and misc
README.md
*.md

# We'll train inside the build, so raw data extras can be excluded if large
# (keep data/heart.csv since train.py needs it during build)
```

---

## Part 3 — Writing the Dockerfile (Line by Line)

Now the main event. Here is our complete Dockerfile, followed by a detailed explanation of **every single line**.

```dockerfile
# ===== 1. Base image =====
FROM python:3.11-slim

# ===== 2. Environment variables =====
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ===== 3. Working directory =====
WORKDIR /app

# ===== 4. System dependencies =====
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# ===== 5. Install Python dependencies (cached layer) =====
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== 6. Copy project files =====
COPY data/ ./data/
COPY train.py .
COPY app.py .

# ===== 7. Train the model during the build =====
RUN python train.py

# ===== 8. Expose the API port =====
EXPOSE 5000

# ===== 9. Start the API when the container runs =====
CMD ["python", "app.py"]
```

---

### Now, Every Line Explained in Plain Words

---

#### Section 1: `FROM python:3.11-slim`

```dockerfile
FROM python:3.11-slim
```

**In plain words:** "Start with a ready-made box that already has Python 3.11 installed on a minimal Linux system."

We don't build everything from scratch. We grab an official Python image as our foundation. The `-slim` part means it's a stripped-down version — it has Python but not a lot of extra tools we don't need, which keeps our final image small (smaller = faster to build, push, and deploy).

*Analogy: Instead of building a kitchen from raw materials, we rent an apartment that already has a stove and sink installed.*

---

#### Section 2: Environment Variables

```dockerfile
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
```

**In plain words:** "Set two rules that make Python behave nicely inside a container."

- `PYTHONUNBUFFERED=1` — Forces Python to print output immediately instead of holding it in a buffer. Without this, your `print()` statements and logs might not show up until the program ends, which makes debugging painful inside Docker.
- `PYTHONDONTWRITEBYTECODE=1` — Stops Python from creating `.pyc` cache files we don't need in a container, keeping things clean.

The `\` at the end of the first line just means "this command continues on the next line" — it's a way to set multiple variables in one instruction.

*Analogy: Posting two house rules on the fridge that every program inside the container follows.*

---

#### Section 3: `WORKDIR /app`

```dockerfile
WORKDIR /app
```

**In plain words:** "Make a folder called `/app` inside the container and work inside it from now on."

Every command after this runs inside `/app`. So when we later copy `train.py`, it lands at `/app/train.py`. This keeps our project organized in one place rather than scattered around the container's filesystem.

*Analogy: Telling everyone "we're working in the kitchen now" so you don't have to specify the location for every single instruction.*

---

#### Section 4: System Dependencies

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*
```

**In plain words:** "Install a Linux system library that scikit-learn needs, then clean up the leftover install files."

Some ML libraries (like scikit-learn) rely on system-level libraries that aren't part of Python. `libgomp1` is one such library (it handles parallel processing). We install it using the Linux package manager `apt-get`.

Breaking it down:
- `apt-get update` — Refresh the list of available system packages.
- `apt-get install -y --no-install-recommends libgomp1` — Install `libgomp1`. The `-y` auto-confirms (says "yes" to prompts), and `--no-install-recommends` avoids installing extra optional packages we don't need.
- `rm -rf /var/lib/apt/lists/*` — Delete the package list cache afterward to keep the image smaller.

We chain these with `&&` so they all happen in **one layer**, which keeps the image lean.

*Analogy: Going to the hardware store for one specific tool your recipe needs, then throwing away the shopping bags so your kitchen stays tidy.*

---

#### Section 5: Install Python Dependencies (The Smart Caching Trick)

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

**In plain words:** "Copy just the requirements list, then install all the Python packages it names."

This is two steps:
- `COPY requirements.txt .` — Copy *only* the `requirements.txt` file into `/app` (the `.` means "here", the current working directory).
- `RUN pip install --no-cache-dir -r requirements.txt` — Install all the packages listed. `--no-cache-dir` tells pip not to keep its download cache, which keeps the image smaller.

**Why copy only requirements.txt first, and not all the code?** This is the single most important Docker best practice. Docker remembers ("caches") each step. Your code changes all the time, but your dependency list rarely changes. By installing dependencies *before* copying your code:
- When you tweak `app.py` and rebuild, Docker sees that `requirements.txt` hasn't changed, so it **reuses the already-installed packages** — rebuild takes seconds.
- If we copied all code first, every tiny code change would force Docker to reinstall every package from scratch — rebuild takes minutes.

*Analogy: Stock your pantry once (slow, but you rarely restock). Then each time you cook, you only grab the fresh ingredients (fast). You don't restock the entire pantry every time you make a sandwich.*

---

#### Section 6: Copy Project Files

```dockerfile
COPY data/ ./data/
COPY train.py .
COPY app.py .
```

**In plain words:** "Now copy the dataset, the training script, and the API script into the container."

- `COPY data/ ./data/` — Copy the `data` folder (containing `heart.csv`) into `/app/data/`.
- `COPY train.py .` — Copy the training script into `/app/`.
- `COPY app.py .` — Copy the API script into `/app/`.

We do this *after* installing dependencies precisely because of the caching reason explained above.

*Analogy: Now that the kitchen is set up and the pantry is stocked, bring in the specific ingredients and the recipe card for tonight's meal.*

---

#### Section 7: Train the Model During Build

```dockerfile
RUN python train.py
```

**In plain words:** "Run the training script right now, while building the image, so the trained model gets baked into the image."

This executes `train.py` during the build. It trains the Random Forest and saves `models/model.pkl` *inside the image*. When someone runs a container from this image, the trained model is already there, ready to serve predictions instantly — no training needed at runtime.

> **Design note:** Training during the build is great for small, fast-training models like this one. For large models that take hours to train, you'd train separately, save the model (e.g., with DVC as in Article 3), and `COPY` the pre-trained model into the image instead of training inside it. For our small project, training in the build is simple and convenient.

*Analogy: Pre-cooking the meal and sealing it in the kit, so the customer just has to reheat it rather than cook from scratch.*

---

#### Section 8: `EXPOSE 5000`

```dockerfile
EXPOSE 5000
```

**In plain words:** "Announce that this container's app listens on port 5000."

Our Flask API runs on port 5000 (we set that in `app.py`). `EXPOSE` documents this. Important: this line is **informational only** — it doesn't actually open the port to your laptop. To truly connect, we use `-p` when running the container (shown in Part 4).

*Analogy: Putting up a sign that says "Service window is at counter 5000." The sign tells people where to go, but you still need to actually open a path to that window (the `-p` flag) for visitors to reach it.*

---

#### Section 9: `CMD ["python", "app.py"]`

```dockerfile
CMD ["python", "app.py"]
```

**In plain words:** "When someone starts a container from this image, automatically run the API server."

`CMD` defines the default action. Here, starting the container launches `app.py`, which starts the Flask server and begins listening for prediction requests. This is the "main purpose" of our container.

*Analogy: The default action when the meal kit is opened — "heat and serve." It's what happens automatically unless you override it.*

---

## Part 4 — Building and Running the Container

Now let's actually use our Dockerfile.

### Step 4.1 — Build the Image

From inside the `heart_disease_docker/` folder:

```bash
docker build -t heart-disease-api:v1 .
```

**Breaking down this command:**
- `docker build` — the command to build an image.
- `-t heart-disease-api:v1` — tag (name) the image `heart-disease-api` with version `v1`.
- `.` — the build context: "find the Dockerfile in the current directory."

**What you'll see:** Docker executes each instruction, showing each step:

```
[+] Building 45.2s
 => [1/8] FROM python:3.11-slim
 => [2/8] WORKDIR /app
 => [3/8] RUN apt-get update && apt-get install...
 => [4/8] COPY requirements.txt .
 => [5/8] RUN pip install --no-cache-dir -r requirements.txt
 => [6/8] COPY data/ ./data/
 => [7/8] COPY train.py . && COPY app.py .
 => [8/8] RUN python train.py
       Model trained. Test accuracy: 0.8525
       Model saved to models/model.pkl
 => exporting to image
 => => naming to docker.io/library/heart-disease-api:v1
```

Notice the training output appears during the build — the model is now baked into the image.

### Step 4.2 — Verify the Image Exists

```bash
docker images
```

```
REPOSITORY           TAG    IMAGE ID       CREATED         SIZE
heart-disease-api    v1     a3f5c2d8e1b9   2 minutes ago   450MB
```

### Step 4.3 — Run the Container

```bash
docker run -d -p 8000:5000 --name heart-api heart-disease-api:v1
```

**Breaking down this command:**
- `docker run` — create and start a container.
- `-d` — detached mode (runs in the background so your terminal is free).
- `-p 8000:5000` — **port mapping**: connect port 8000 on your laptop to port 5000 inside the container. This is the actual "door" that `EXPOSE` only advertised.
- `--name heart-api` — give the container a friendly name.
- `heart-disease-api:v1` — the image to run.

> **The port mapping explained:** Your Flask app listens on port 5000 *inside* the container. But "inside the container" is isolated from your laptop. The `-p 8000:5000` builds a bridge: requests to `localhost:8000` on your laptop get forwarded to port 5000 in the container. You could map to any host port — `-p 9999:5000` would let you use `localhost:9999`.

### Step 4.4 — Confirm It's Running

```bash
docker ps
```

```
CONTAINER ID   IMAGE                  STATUS         PORTS                    NAMES
b1e2d4f6a8c0   heart-disease-api:v1   Up 10 seconds  0.0.0.0:8000->5000/tcp   heart-api
```

---

## Part 5 — Testing the Containerized API

### Step 5.1 — Health Check

```bash
curl http://localhost:8000/health
```

```json
{"status": "healthy"}
```

The API is alive and responding from inside the container.

### Step 5.2 — Make a Prediction

Send a patient's data to the prediction endpoint:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
    "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
    "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1
  }'
```

**Response:**

```json
{
  "prediction": 1,
  "probability": 0.78,
  "interpretation": "Heart disease likely"
}
```

🎉 Your ML model is now running inside a Docker container, serving predictions over HTTP. You can ship this image to any machine with Docker and it will run **exactly the same way**.

---

## Part 6 — Useful Operations on Your Running Container

### View Logs

```bash
docker logs heart-api
# See the Flask startup output and any request logs
```

### Open a Shell Inside the Container (for Debugging)

```bash
docker exec -it heart-api /bin/bash
# Now you're inside the container's Linux shell
# Try: ls /app  → you'll see your files, including models/model.pkl
# Type 'exit' to leave
```

### Stop and Remove

```bash
# Stop the container
docker stop heart-api

# Remove it
docker rm heart-api

# Remove the image if you want
docker rmi heart-disease-api:v1
```

---

## Part 7 — Sharing Your Image

To let others run your exact containerized model, push it to Docker Hub.

```bash
# 1. Log in to Docker Hub
docker login

# 2. Tag the image with your Docker Hub username
docker tag heart-disease-api:v1 yourusername/heart-disease-api:v1

# 3. Push it
docker push yourusername/heart-disease-api:v1
```

Now anyone, anywhere, can run your model with two commands:

```bash
docker pull yourusername/heart-disease-api:v1
docker run -d -p 8000:5000 yourusername/heart-disease-api:v1
```

No "install Python," no "pip install," no "it works on my machine." It just runs. **This is the entire point of Docker.**

---

## Part 8 — Handling Data and Models with Volumes (Advanced Note)

In our project we baked the model into the image. But sometimes you want data or models to live *outside* the container so they persist and can be swapped without rebuilding. That's what **volumes** are for.

For example, to mount a local `models` folder into the container instead of baking the model in:

```bash
docker run -d -p 8000:5000 \
  -v $(pwd)/models:/app/models \
  --name heart-api \
  heart-disease-api:v1
```

The `-v $(pwd)/models:/app/models` part connects your laptop's `models` folder to `/app/models` inside the container. Now you can update the model file on your laptop and the container sees the new version — no rebuild needed.

*Analogy: Instead of sealing the food inside the kit, you give the container access to your fridge (a volume) so it can use whatever's currently inside.*

This connects beautifully to Article 3: you'd version your data and models with **DVC**, `dvc pull` them onto the host, then mount them into the container as a volume. Git versions code, DVC versions data/models, and Docker packages the runtime — together they form a complete, reproducible ML workflow.

---

## Summary

You've now containerized a real ML project from scratch:

✅ Built a working ML project — training script + prediction API  
✅ Wrote a complete Dockerfile and understood **every single line** in plain words  
✅ Learned the critical layer-caching trick (copy requirements before code)  
✅ Built an image, ran a container, and mapped ports correctly  
✅ Tested a live prediction API running inside Docker  
✅ Learned to share images via Docker Hub  
✅ Saw how volumes connect Docker back to Git and DVC for a full workflow  

### The Complete Picture (Across the Whole Series)

You now have all the pieces of professional, reproducible machine learning:

| Tool | What it versions / does |
|------|------------------------|
| **Git** | Your code |
| **GitHub** | Cloud collaboration & sharing of code |
| **DVC** | Your data and models |
| **Docker** | Your entire runtime environment |

Together, these guarantee that your ML project runs identically everywhere, that every experiment is reproducible, and that you can hand your work to anyone — a teammate, a server, or your future self — and it will just work.

### Where to Go Next

- **Docker Compose** — run your model API alongside a database or frontend with one command
- **Multi-stage builds** — make production images even smaller by separating build and runtime stages
- **GPU containers** — use `nvidia-docker` and CUDA base images for deep learning
- **Kubernetes** — orchestrate and scale many containers across a cluster for production deployment
- **CI/CD** — automatically build and deploy your Docker image on every Git push using GitHub Actions

You've gone from raw code to a fully versioned, reproducible, containerized ML service. That's the foundation of real-world MLOps.
