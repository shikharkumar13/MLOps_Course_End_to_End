# Article 7: FastAPI & Pydantic for ML Deployment — From Theory to a Working Project

*What an API really is, how endpoints work, why ML deployment needs them, and how FastAPI + Pydantic make serving models clean and safe*

---

## Introduction

In Article 6 you learned Flask — a simple, reliable way to serve a model. Now we level up to **FastAPI**, the framework that has become the default choice for ML APIs in industry. But before we touch FastAPI, we need to step back and answer a more fundamental question that we've been using loosely for several articles: **what actually *is* an API?**

This article builds from the ground up. We'll define what an API is, what endpoints are and why they exist, how an ML model uses all of this to get deployed, and then introduce **FastAPI** and its companion **Pydantic** — the tool that makes your API validate input automatically so bad data never reaches your model. We finish with a complete, practical heart disease project that connects to everything you've built so far in this series.

---

## 📋 Learning Roadmap

| # | Topic |
|---|-------|
| 1 | What is an API? (the foundational concept) |
| 2 | What are API endpoints, and why do they exist? |
| 3 | How an API works: the request-response model |
| 4 | How ML deployment uses an API |
| 5 | What is FastAPI and why prefer it over Flask? |
| 6 | What is Pydantic and the problem it solves |
| 7 | How Pydantic and FastAPI work together |
| 8 | Practical: a complete heart disease FastAPI project |
| 9 | Interactive docs, testing, and Docker integration |

---

## Part 1 — What Is an API?

**API** stands for **Application Programming Interface**. That name sounds intimidating, so let's strip it down: an API is simply **a defined way for two pieces of software to talk to each other.**

That's it. It's a contract: "If you send me a request in *this* format, I'll send you back a response in *that* format." Neither side needs to know how the other works internally — they just need to agree on the format of the conversation.

### The Restaurant Menu Analogy

Imagine you walk into a restaurant. You don't go into the kitchen, inspect the ingredients, and instruct the chef on technique. Instead, there's a **menu**.

- The **menu** lists exactly what you can order and how to order it.
- You place an order based on the menu.
- The kitchen (which you never see) prepares your dish.
- The waiter brings back exactly what the menu promised.

**The menu is the API.** It's the agreed-upon interface between you (one piece of software) and the kitchen (another piece of software). You don't need to know *how* the kitchen works — you just need to know what's on the menu and how to order.

### The Wall Socket Analogy

Here's another angle. Think of an electrical wall socket. Any device with the right plug can draw power — a lamp, a laptop charger, a phone. The socket doesn't care what device you plug in, and the device doesn't care how the power plant generates electricity. The **socket is a standardized interface** between the power grid and your devices.

An API is that socket for software. It's a standard plug point that lets different programs connect and exchange information without knowing each other's internal details.

### Why APIs Matter

APIs are everywhere and they're the reason modern software works:

- When a weather app shows the forecast, it's calling a weather service's API.
- When you "Log in with Google" on a website, that site is calling Google's API.
- When your ML model serves a prediction to a mobile app, the app is calling **your** API.

APIs let software be built from independent, interchangeable parts that communicate through clear contracts — the same way the shipping containers in Article 4 let global trade work through a standard interface.

---

## Part 2 — What Are API Endpoints, and Why Do They Exist?

An API usually offers more than one service. An **endpoint** is a specific address within your API that performs one specific job.

### Back to the Menu

If the API is the whole menu, then each **endpoint is a single item on that menu**. A restaurant menu has sections — appetizers, mains, desserts. You order from a specific item, not "the menu" as a whole.

Your ML API might have endpoints like:
- `/health` — "are you running?"
- `/predict` — "give me a prediction for this data"
- `/model-info` — "tell me about the current model version"

Each endpoint is a distinct address that does one well-defined thing.

### What Problem Do Endpoints Solve?

Endpoints solve the problem of **organizing and separating different capabilities** of your service. Without them, you'd have one giant tangled function trying to do everything. With endpoints:

- Each capability has its own clear address.
- Clients ask for exactly what they need.
- You can update, secure, or monitor each capability independently.

```
       Your ML API (the whole menu)
                  │
      ┌───────────┼────────────┐
      │           │            │
  /health     /predict    /model-info
  (am I up?)  (predict!)  (which model?)
      │           │            │
   simple      runs the    returns
   check       model       metadata
```

### Anatomy of an Endpoint

An endpoint is defined by two things working together:

1. **A path** — the address, like `/predict`.
2. **An HTTP method** — the *kind* of action: GET (fetch something), POST (send data and act on it), and others like PUT/DELETE for updating/removing.

So `POST /predict` is a complete endpoint: "send data to the `/predict` address to get a prediction." For ML, you mostly use **GET** for simple reads and **POST** for predictions (since you're *sending* the model input data).

*Analogy: The path is the room number; the method is what you intend to do there — visit (GET) or deliver a package (POST).*

---

## Part 3 — How an API Works: The Request-Response Model

Every API interaction follows the same loop you saw in Article 6, but let's formalize it because it's the heartbeat of all web APIs.

```
   CLIENT                                   SERVER (your API)
      │                                            │
      │  ── REQUEST ──►                            │
      │    • method: POST                          │
      │    • path:   /predict                      │
      │    • headers: "Content-Type: JSON"         │
      │    • body:   {"age": 63, "chol": 233, ...} │
      │                                            │
      │                                  processes the request:
      │                                  validates → runs model → builds reply
      │                                            │
      │  ◄── RESPONSE ──                           │
      │    • status: 200 OK                        │
      │    • body:   {"prediction": 1, ...}        │
      │                                            │
```

### The Two Halves

**The Request** (client → server) contains:
- The **method** (POST) and **path** (`/predict`)
- **Headers** — metadata, like what format the body is in
- The **body** — the actual data (the patient's features as JSON)

**The Response** (server → client) contains:
- A **status code** — a number signaling what happened
- The **body** — the result (the prediction as JSON)

### Status Codes (Just the Ones You Need)

Status codes are the server's way of saying how the request went. You'll mainly encounter:

| Code | Meaning | When |
|------|---------|------|
| **200** | OK | Everything worked |
| **422** | Unprocessable Entity | The input data was invalid (FastAPI sends this automatically) |
| **404** | Not Found | The endpoint address doesn't exist |
| **500** | Internal Server Error | Your code crashed |

*Analogy: Status codes are like a delivery confirmation — "delivered" (200), "wrong address" (404), "package was damaged/unreadable" (422), or "the warehouse caught fire" (500).*

---

## Part 4 — How ML Deployment Uses an API

Now we connect this to machine learning. **Deploying** a model means making it available for others to use. An API is the standard way to do that.

### The Full Picture

```
┌─────────────┐         ┌──────────────────────────────────┐
│   CLIENT    │         │       YOUR ML API SERVER          │
│             │         │  ┌────────────────────────────┐  │
│ web app /   │ ──POST──┼─►│ 1. Endpoint receives data  │  │
│ mobile app /│ /predict│  │ 2. Validate the input      │  │
│ other code  │         │  │ 3. Format for the model    │  │
│             │         │  │ 4. model.predict()         │  │
│             │ ◄──JSON─┼──│ 5. Return prediction       │  │
└─────────────┘         │  └────────────────────────────┘  │
                        │     ▲                             │
                        │     │ loaded once at startup      │
                        │  ┌──────────────┐                 │
                        │  │  model.pkl   │                 │
                        │  └──────────────┘                 │
                        └──────────────────────────────────┘
```

### The Components Attached to an ML API

A production ML API isn't just a prediction function. Several components work together:

1. **The model artifact** — your trained `model.pkl` (versioned with DVC, from Article 3), loaded once at startup.
2. **The endpoints** — `/predict` for inference, `/health` for monitoring.
3. **Input validation** — checking the incoming data is correct *before* it reaches the model (this is where Pydantic shines).
4. **Preprocessing** — transforming raw input into the exact format the model expects.
5. **The response formatter** — packaging the prediction into clean JSON.
6. **The web server** — the framework (FastAPI) plus a production server (Uvicorn/Gunicorn) that handles the networking.

This article's job is to show how **FastAPI** ties components 2, 5, and 6 together, and how **Pydantic** handles component 3 elegantly.

---

## Part 5 — What Is FastAPI and Why Prefer It Over Flask?

**FastAPI** is a modern Python web framework for building APIs. Like Flask, it lets you define endpoints with Python functions. Unlike Flask, it was designed specifically for building APIs and comes with powerful features built in.

### What FastAPI Gives You That Flask Doesn't

| Feature | Flask | FastAPI |
|---------|-------|---------|
| Define endpoints with functions | ✅ | ✅ |
| Automatic input validation | ❌ (manual) | ✅ (via Pydantic) |
| Automatic interactive API docs | ❌ | ✅ (built-in) |
| Data type checking | ❌ | ✅ |
| Async support (high concurrency) | Limited | ✅ Native |
| Helpful auto error messages | ❌ | ✅ |

The two standout features for ML are **automatic input validation** and **automatic interactive documentation**. With Flask, if a client sends `"age": "sixty-three"` (a string instead of a number), your model might crash with a confusing error deep inside scikit-learn. With FastAPI + Pydantic, the bad input is caught at the door, and the client gets a clear message explaining exactly what was wrong — before your model ever sees it.

*Analogy: Flask is a capable but bare kitchen — you do all the quality control yourself. FastAPI comes with a built-in inspector at the door who checks every order for correctness, plus a printed, always-up-to-date menu that customers can browse interactively.*

### A Minimal FastAPI App

```python
from fastapi import FastAPI

# Create the application (just like Flask)
app = FastAPI()

# Define an endpoint with a decorator
@app.get("/health")
def health():
    return {"status": "healthy"}
```

Two differences from Flask jump out:
- The decorator is `@app.get(...)` — the HTTP method is part of the decorator itself (Flask used `methods=["GET"]`). For POST you'd write `@app.post(...)`.
- You return a plain Python dictionary — FastAPI **automatically converts it to JSON**. No `jsonify` needed.

### Running a FastAPI App

FastAPI doesn't have a built-in `app.run()`. Instead you run it with **Uvicorn**, a fast server designed for it:

```bash
pip install fastapi uvicorn

# Run the app: "main:app" means the 'app' object in main.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- `main:app` — file `main.py`, the FastAPI object named `app`.
- `--host 0.0.0.0` — reachable from outside (same reason as in Article 6).
- `--reload` — auto-restart when you edit code (development only; drop it in production).

---

## Part 6 — What Is Pydantic and the Problem It Solves

**Pydantic** is a Python library for **data validation**. It lets you define the *shape* of your data — what fields exist and what types they should be — and then it automatically checks that incoming data matches.

### The Problem Pydantic Solves

Recall the messy reality of receiving data from the outside world. A client is supposed to send:

```json
{"age": 63, "chol": 233}
```

But clients make mistakes. They might send:

```json
{"age": "sixty-three", "chol": 233}     ← age is text, not a number
{"chol": 233}                            ← age is missing entirely
{"age": 63, "cholesterol": 233}          ← wrong field name
```

Without validation, this bad data flows straight into your model and causes a cryptic crash — or worse, a silently wrong prediction. With Flask, you'd write defensive code by hand to check every field. That's tedious and error-prone.

**Pydantic does this checking for you, automatically.** You declare what valid data looks like once, and Pydantic enforces it on every request.

### How You Define Data with Pydantic

You create a class that inherits from Pydantic's `BaseModel` and declare each field with its type:

```python
from pydantic import BaseModel

class PatientData(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int
```

This class is a **schema** — a precise description of what valid patient data looks like. Each line says "this field must exist and must be this type." `age: int` means age must be a whole number; `oldpeak: float` means it can have decimals.

*Analogy: Pydantic is a strict form with labeled boxes. Each box is labeled with what belongs in it ("Age — numbers only"). If someone writes letters in the age box or leaves it blank, the form is rejected before it's processed.*

### Adding Constraints with `Field`

You can go further and set rules on values, not just types, using `Field`:

```python
from pydantic import BaseModel, Field

class PatientData(BaseModel):
    age: int = Field(..., ge=0, le=120)        # ge = >=0, le = <=120
    sex: int = Field(..., ge=0, le=1)          # must be 0 or 1
    chol: int = Field(..., gt=0)               # must be greater than 0
    oldpeak: float = Field(..., ge=0)
```

- `...` means the field is **required**.
- `ge` = greater-than-or-equal, `le` = less-than-or-equal, `gt` = greater-than.

Now Pydantic rejects an `age` of 200 or a negative cholesterol automatically. This is incredibly valuable for ML — it stops physically impossible or out-of-range inputs from ever reaching your model.

---

## Part 7 — How Pydantic and FastAPI Work Together

Here's the magic: FastAPI is built on Pydantic. When you use a Pydantic model as the type of an endpoint's parameter, FastAPI **automatically**:

1. Reads the incoming JSON
2. Validates it against your Pydantic schema
3. If invalid → sends back a clear 422 error explaining what's wrong (you write zero code for this)
4. If valid → hands your function a clean, typed object to use

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PatientData(BaseModel):
    age: int
    chol: int

@app.post("/predict")
def predict(patient: PatientData):    # ← the Pydantic model as the parameter type
    # If we reach this line, the data is GUARANTEED valid.
    # 'patient' is a clean object: patient.age, patient.chol
    return {"received_age": patient.age, "received_chol": patient.chol}
```

The single line `def predict(patient: PatientData):` is doing enormous work. By annotating the parameter with the Pydantic class, you've told FastAPI: "the body of this request must match the `PatientData` schema." FastAPI handles all validation automatically.

**Compare the two approaches:**

```python
# Flask — manual validation (verbose, easy to forget cases)
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if "age" not in data:
        return jsonify({"error": "age is required"}), 400
    if not isinstance(data["age"], int):
        return jsonify({"error": "age must be an integer"}), 400
    # ... repeat for all 13 fields ...

# FastAPI — automatic validation (declare once, done)
@app.post("/predict")
def predict(patient: PatientData):
    # validation already happened; just use the data
    ...
```

*Analogy: Flask makes you personally inspect every order at the counter, checking each item by hand. FastAPI + Pydantic is like having an automated inspection gate — you describe the rules once, and every order is checked automatically before it reaches you.*

---

## Part 8 — Practical: A Complete Heart Disease FastAPI Project

Let's build the full project, reusing the heart disease model from earlier articles. This connects directly to your Git (Articles 1–2), DVC (Article 3), and Docker (Articles 4–5) work.

### Project Structure

```
heart_disease_fastapi/
├── Dockerfile
├── requirements.txt
├── train.py                 ← trains and saves the model
├── main.py                  ← the FastAPI app
├── schemas.py               ← Pydantic models (input/output schemas)
├── data/
│   └── heart.csv
└── models/
    └── model.pkl
```

### Step 8.1 — Requirements

**`requirements.txt`:**

```
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.4
joblib==1.3.2
fastapi==0.110.0
uvicorn==0.29.0
pydantic==2.6.0
```

### Step 8.2 — Training Script

**`train.py`** (same idea as before — trains and saves the model):

```python
"""train.py — Train the heart disease model and save it."""
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv("data/heart.csv")
X = df.drop(columns=["target"])
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(X_train, y_train)

acc = accuracy_score(y_test, model.predict(X_test))
print(f"Model trained. Test accuracy: {acc:.4f}")

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.pkl")
print("Model saved to models/model.pkl")
```

### Step 8.3 — The Pydantic Schemas

**`schemas.py`** — defines what valid input and output look like:

```python
"""schemas.py — Pydantic models for request validation and response shape."""
from pydantic import BaseModel, Field


class PatientData(BaseModel):
    """Schema for a single patient's input features."""
    age: int = Field(..., ge=0, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="1 = male, 0 = female")
    cp: int = Field(..., ge=0, le=3, description="Chest pain type (0-3)")
    trestbps: int = Field(..., gt=0, description="Resting blood pressure")
    chol: int = Field(..., gt=0, description="Serum cholesterol in mg/dl")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG results")
    thalach: int = Field(..., gt=0, description="Max heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise-induced angina")
    oldpeak: float = Field(..., ge=0, description="ST depression")
    slope: int = Field(..., ge=0, le=2, description="Slope of ST segment")
    ca: int = Field(..., ge=0, le=4, description="Number of major vessels")
    thal: int = Field(..., ge=0, le=3, description="Thalassemia type")

    # An example shown in the interactive docs
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
                "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
                "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1
            }]
        }
    }


class PredictionResponse(BaseModel):
    """Schema for the prediction we send back."""
    prediction: int
    probability: float
    interpretation: str
```

Notice we define **both** the input (`PatientData`) and the output (`PredictionResponse`). Defining the response schema lets FastAPI document and validate what your API returns, too.

### Step 8.4 — The FastAPI App

**`main.py`** — the heart of the project:

```python
"""main.py — FastAPI app serving heart disease predictions."""
import joblib
import pandas as pd
from fastapi import FastAPI
from schemas import PatientData, PredictionResponse

# ── Create the app with metadata (shows up in the docs) ──
app = FastAPI(
    title="Heart Disease Prediction API",
    description="Predicts heart disease risk from patient health data.",
    version="1.0.0",
)

# ── Load the model ONCE at startup ──
model = joblib.load("models/model.pkl")

# The exact feature order the model was trained on
FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]


@app.get("/health")
def health():
    """Confirm the API is running."""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
def predict(patient: PatientData):
    """Predict heart disease for one patient."""
    # 'patient' is already validated by Pydantic. Convert it to a dict.
    data = patient.model_dump()

    # Build a DataFrame in the exact feature order the model expects
    input_df = pd.DataFrame([[data[f] for f in FEATURES]], columns=FEATURES)

    # Predict (convert numpy types to plain Python types for JSON)
    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])

    return PredictionResponse(
        prediction=prediction,
        probability=round(probability, 4),
        interpretation="Heart disease likely" if prediction == 1
                        else "Heart disease unlikely",
    )
```

### Walking Through `main.py`

**`app = FastAPI(title=..., ...)`** — creates the app. The `title`, `description`, and `version` automatically appear in the interactive documentation (a nice touch Flask doesn't offer).

**`model = joblib.load(...)`** — loads the model once at startup, outside any function. Same critical rule as Article 6: never load per-request.

**`@app.get("/health")`** — a simple GET endpoint for monitoring. Returns a dict, auto-converted to JSON.

**`@app.post("/predict", response_model=PredictionResponse)`** — the prediction endpoint. Two things to notice:
- `patient: PatientData` — FastAPI validates the incoming JSON against the `PatientData` schema automatically. If it's invalid, the client gets a clear 422 error and your function never runs.
- `response_model=PredictionResponse` — tells FastAPI the shape of the response, which it documents and validates.

**`patient.model_dump()`** — converts the validated Pydantic object back into a plain dictionary so we can rearrange it for the model. (In Pydantic v2 this is `model_dump()`; older v1 code used `.dict()`.)

The rest mirrors what you already know: arrange features in order, predict, convert numpy types, return.

---

## Part 9 — Interactive Docs, Testing, and Docker

### The Killer Feature: Automatic Interactive Docs

Start the app:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Now open **`http://localhost:8000/docs`** in your browser. FastAPI has **automatically generated a complete, interactive documentation page** — with no extra code from you. You'll see both endpoints, the exact input schema (with your field descriptions and the example), and a "Try it out" button that lets you send real requests right from the browser.

This page (called Swagger UI) is generated from your Pydantic schemas and endpoint definitions. It's a massive productivity win: your API documents itself, stays in sync automatically, and lets anyone test it without writing code.

*Analogy: Remember the restaurant menu? FastAPI prints a beautiful, always-accurate menu for you automatically — and even lets customers place test orders directly from the menu to see what comes back.*

There's also `http://localhost:8000/redoc` for an alternative documentation style.

### Testing the API

**With curl:**

```bash
# Health check
curl http://localhost:8000/health

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233, "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1}'
```

**Response:**

```json
{
  "prediction": 1,
  "probability": 0.78,
  "interpretation": "Heart disease likely"
}
```

**Watch validation work** — send a bad request (age as text):

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": "old", "sex": 1, "cp": 3, "trestbps": 145, "chol": 233, "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1}'
```

FastAPI automatically rejects it with a clear 422 error:

```json
{
  "detail": [{
    "type": "int_parsing",
    "loc": ["body", "age"],
    "msg": "Input should be a valid integer, unable to parse string as an integer"
  }]
}
```

You wrote **zero** validation code for this. Pydantic and FastAPI handled it entirely. The error even tells the client exactly which field (`age`) and what was wrong.

### Dockerizing the FastAPI App

This connects directly to Articles 4 and 5. The Dockerfile is nearly identical — only the final command changes, because we now run with Uvicorn instead of `python app.py`:

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies first (layer caching, from Article 4)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY data/ ./data/
COPY train.py schemas.py main.py ./

# Train the model during the build
RUN python train.py

# Document the port
EXPOSE 8000

# Run with Uvicorn (the FastAPI server)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

The only meaningful change from Article 5's Dockerfile is the final `CMD` line — instead of `python app.py`, we launch Uvicorn pointing at our FastAPI `app`. Everything you learned about layer caching, `EXPOSE`, and base images carries over unchanged.

**Build and run:**

```bash
docker build -t heart-disease-fastapi:v1 .
docker run -d -p 8000:8000 --name heart-fastapi heart-disease-fastapi:v1
```

Then visit `http://localhost:8000/docs` — your containerized, self-documenting, input-validating ML API is live.

> **Production note (from Article 6):** For heavy traffic, run Uvicorn with multiple workers, often managed by Gunicorn:
> ```dockerfile
> CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
> ```
> This combines Gunicorn's robust process management with Uvicorn's speed — the standard production setup for FastAPI.

---

## Summary

You've now mastered APIs and FastAPI for ML deployment:

✅ **What an API is** — a standard contract for software to communicate (the menu, the wall socket)  
✅ **What endpoints are** — specific addresses for specific jobs, and why they organize a service  
✅ **The request-response model** — methods, headers, body, and status codes  
✅ **How ML deployment uses APIs** — and the components that make up a real ML API  
✅ **FastAPI** — modern, with automatic validation and self-generating docs, and why it's preferred over Flask  
✅ **Pydantic** — declare your data's shape once, get automatic validation for free (the strict labeled form)  
✅ **FastAPI + Pydantic together** — clean, safe endpoints where bad data never reaches your model  
✅ **A complete practical project** — schemas, app, interactive docs, testing, and Docker integration  

### Flask vs FastAPI: Which to Use?

Both are excellent. Use **Flask** when you want maximum simplicity and minimal dependencies for a tiny service. Use **FastAPI** when you want automatic validation, self-documenting endpoints, and async performance — which is most serious ML deployments today. FastAPI has become the industry default for ML APIs largely because of the Pydantic validation and the free interactive docs.

### The Complete Series, Connected

| Tool | Role | Article |
|------|------|---------|
| **Git / GitHub** | Version and share code | 1, 2 |
| **DVC** | Version data and models | 3 |
| **Docker** | Package the app + environment | 4, 5 |
| **Flask** | Simple model API | 6 |
| **FastAPI + Pydantic** | Robust, validated, documented model API | 7 (this one) |

The end-to-end workflow now reads cleanly: write model code (**Git**), version your data and trained models (**DVC**), wrap the model in a validated, self-documenting API (**FastAPI + Pydantic**), package it into a portable container (**Docker**), and serve it in production (**Uvicorn + Gunicorn**).

### Where to Go Next

- **Background tasks** — handle slow operations without blocking the response
- **Dependency injection** — FastAPI's system for sharing resources (like the model) cleanly across endpoints
- **Authentication** — protect your API with API keys or OAuth before going public
- **Model versioning in the API** — serve multiple model versions behind different endpoints
- **Cloud deployment** — push your container to AWS, GCP, or Azure and expose it to the world

You can now turn any trained model into a professional, production-ready API — validated, documented, containerized, and ready to serve real users. That's the complete deployment story this series set out to teach.
