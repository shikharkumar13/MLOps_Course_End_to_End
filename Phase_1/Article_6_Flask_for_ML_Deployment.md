# Article 6: Flask for ML Deployment — Just Enough to Serve Your Model

*Understanding how Flask works and exactly what to write to turn a trained model into a working API*

---

## Introduction

In Article 5, we used Flask to wrap our heart disease model in an API — but we breezed past *how* Flask actually works. This article fills that gap. By the end, you'll understand Flask well enough to take any trained model and expose it as a web service that other programs (or people) can send data to and get predictions back from.

We're not going to cover everything Flask can do — Flask is a full web framework and you could write a whole book on it. Instead, we cover **exactly the parts an ML practitioner needs** to deploy a model, and nothing more. This is the "just enough Flask" article.

---

## 📋 Learning Roadmap

| # | Topic |
|---|-------|
| 1 | Why does an ML model need a web framework at all? |
| 2 | What is Flask and how does it work? |
| 3 | The request-response cycle (the core idea) |
| 4 | Routes, methods, and endpoints |
| 5 | Handling input: JSON requests |
| 6 | Sending output: JSON responses |
| 7 | The complete ML serving pattern |
| 8 | Testing your API |
| 9 | Production notes (Gunicorn, why `app.run()` isn't enough) |

---

## Part 1 — Why Does an ML Model Need a Web Framework?

You've trained a model. It lives in a `model.pkl` file. You can load it in a Python script and call `model.predict()`. So why complicate things with Flask?

### The Problem: A Model File Is Not Usable by Others

Think about who needs to *use* your model:

- A **website** where users enter their health data and see a risk score
- A **mobile app** that sends sensor readings and gets predictions
- Another **team's software** that needs your fraud-detection score
- A **business dashboard** pulling live predictions

None of these are Python scripts running on your laptop. They are separate programs, often on different machines, sometimes written in different languages entirely. They cannot just `import joblib` and load your `.pkl` file. They need a **standard way to ask your model a question and get an answer.**

### The Restaurant Analogy

Imagine your trained model is a **skilled chef** locked in a kitchen.

- The chef can cook brilliantly, but customers can't walk into the kitchen and talk to the chef directly — that would be chaos.
- What you need is a **waiter and a service window**: customers place an order (send data) at the window, the order goes to the chef (your model), and the finished dish (the prediction) comes back out the window.

**Flask is that waiter and service window.** It stands between the outside world and your model. It accepts requests in a standard format (HTTP), passes the data to your model, and sends the prediction back — all over the web, so *any* program from *anywhere* can use your model.

### What "Serving a Model" Means

Turning a model file into a live, callable service is called **serving** or **deploying** the model. Flask is one of the simplest tools to do this in Python.

```
Before Flask:                      After Flask:
┌──────────────┐                   ┌──────────────┐   HTTP    ┌─────────────┐
│  model.pkl   │                   │  Any client  │ ────────► │   Flask     │
│  (a file you │                   │  (web app,   │           │   + model   │
│   can only   │                   │  mobile,     │ ◄──────── │   (API)     │
│   use in     │                   │  other code) │  prediction│            │
│   Python)    │                   └──────────────┘           └─────────────┘
└──────────────┘
   isolated                              accessible to the whole world
```

---

## Part 2 — What Is Flask and How Does It Work?

**Flask** is a lightweight Python web framework. "Lightweight" means it gives you the essentials to build a web service without forcing a lot of structure on you — perfect for ML APIs, where you often just need a couple of endpoints.

### What Flask Actually Does

At its core, Flask does one simple thing: **it listens for incoming web requests and runs your Python function to respond to them.**

That's it. You write Python functions, you tell Flask "when a request comes to *this* address, run *this* function," and Flask handles all the messy networking details — listening on a port, parsing the HTTP request, sending the response back.

### The Minimal Flask App

Here is the smallest possible Flask application:

```python
from flask import Flask

# 1. Create the Flask application object
app = Flask(__name__)

# 2. Define a route: "when someone visits '/', run this function"
@app.route("/")
def home():
    return "Hello, my model is alive!"

# 3. Start the server
if __name__ == "__main__":
    app.run()
```

Run it with `python app.py`, open `http://localhost:5000` in your browser, and you'll see your message. Let's unpack each piece because every Flask app — including complex ML ones — is built on these exact three steps.

**Step 1: `app = Flask(__name__)`**
This creates your application. `__name__` is a special Python variable that tells Flask where the app is located (so it can find files relative to it). You'll write this line in every Flask app, essentially unchanged.

*Analogy: Opening the restaurant and hanging up the "We're Open" sign.*

**Step 2: `@app.route("/")`**
This is a **decorator** (the `@` symbol) that connects a web address to a function. It says "when a request comes to the address `/`, run the function below it." The `/` is the root address (like the homepage).

*Analogy: Posting a menu that says "if a customer asks for the homepage, the waiter does this."*

**Step 3: `app.run()`**
This starts the web server, which begins listening for requests. Without this, nothing happens.

*Analogy: Unlocking the door and letting customers in.*

---

## Part 3 — The Request-Response Cycle (The Core Idea)

Everything in Flask revolves around one fundamental pattern: a **request** comes in, your code runs, and a **response** goes out. Understanding this cycle is understanding Flask.

```
   CLIENT                          FLASK SERVER
(browser, app,                    (your Python code)
 other program)
      │                                  │
      │   1. REQUEST                      │
      │   "POST /predict                  │
      │    here's patient data"           │
      │ ────────────────────────────────►│
      │                                  │  2. Flask matches the address
      │                                  │     to your function and runs it
      │                                  │
      │                                  │  3. Your function loads the data,
      │                                  │     calls model.predict(),
      │                                  │     builds an answer
      │                                  │
      │   4. RESPONSE                     │
      │   "prediction: 1,                 │
      │    probability: 0.78"             │
      │ ◄────────────────────────────────│
      │                                  │
```

For an ML API, this cycle is:
1. A client sends patient/customer data to your prediction address.
2. Flask receives it and runs your prediction function.
3. Your function feeds the data to the model and gets a prediction.
4. Flask sends that prediction back to the client.

Everything else in this article is just detail layered on top of this simple loop.

### A Quick Word on HTTP Methods

When a client makes a request, it uses a **method** that signals intent. You only need two for ML:

- **GET** — "give me something" (used for simple checks, like "are you alive?"). This is what your browser uses when you visit a URL.
- **POST** — "here's some data, do something with it" (used for predictions, because the client is *sending* data — the patient's measurements).

*Analogy: GET is asking the waiter "are you open?" POST is handing the waiter your order with all the details.*

For predictions we use **POST**, because the client needs to send the input features to the model.

---

## Part 4 — Routes, Methods, and Endpoints

A **route** (also called an **endpoint**) is a specific address in your API paired with the function that handles it. An ML API typically has just two or three.

```python
from flask import Flask

app = Flask(__name__)

# A health-check endpoint (GET) — confirms the API is running
@app.route("/health", methods=["GET"])
def health():
    return "OK"

# A prediction endpoint (POST) — does the actual ML work
@app.route("/predict", methods=["POST"])
def predict():
    return "prediction goes here"
```

**Breaking it down:**
- `@app.route("/health", methods=["GET"])` — defines an endpoint at the address `/health` that only responds to GET requests.
- `@app.route("/predict", methods=["POST"])` — defines an endpoint at `/predict` that only responds to POST requests.
- The `methods=[...]` part lists which HTTP methods that endpoint accepts. If you omit it, Flask assumes GET only.

**Why have a `/health` endpoint?** In real deployments, monitoring systems and container orchestrators (like Kubernetes, or Docker's health checks) periodically ping `/health` to confirm your service is alive. It's a tiny endpoint but a professional standard. (We used exactly this in Article 5.)

*Analogy: `/health` is the "Are you open?" sign customers can check. `/predict` is the actual service counter where the real work happens.*

---

## Part 5 — Handling Input: JSON Requests

For ML, clients send input data as **JSON** — a simple, universal text format that looks like a Python dictionary. This is how a client sends one patient's data:

```json
{
  "age": 63,
  "sex": 1,
  "cp": 3,
  "trestbps": 145,
  "chol": 233
}
```

### Reading JSON in Flask

Flask gives you a `request` object that holds everything about the incoming request. To read the JSON the client sent:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    # Get the JSON data the client sent
    data = request.get_json()

    # Now 'data' is a Python dictionary you can use
    age = data["age"]
    chol = data["chol"]
    # ... and so on

    return f"Received age={age}, chol={chol}"
```

**The key line is `data = request.get_json()`.** This takes the raw JSON from the request and converts it into a normal Python dictionary. From there you handle it like any dictionary.

*Analogy: The waiter takes the customer's written order (JSON) and reads it out in a form the chef understands (a Python dictionary).*

> **Important:** You must `from flask import request` to use this. The `request` object is automatically available inside your route functions — it represents the *current* incoming request.

---

## Part 6 — Sending Output: JSON Responses

Just as input comes in as JSON, you should send predictions back as JSON. Flask's `jsonify` function does this cleanly — it converts a Python dictionary into a proper JSON response.

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # (model prediction logic would go here)
    prediction = 1
    probability = 0.78

    # Convert a Python dict into a JSON response
    return jsonify({
        "prediction": prediction,
        "probability": probability,
        "interpretation": "Heart disease likely"
    })
```

**The key line is `return jsonify({...})`.** You build a Python dictionary with your results and `jsonify` turns it into JSON that any client can read.

*Analogy: The chef plates the finished dish (jsonify) so it's presented in a standard way the customer expects, rather than handing them a messy pot.*

> **Why not just `return {...}`?** Modern Flask can auto-convert a dictionary to JSON, so `return {...}` often works too. But `jsonify` is explicit, handles edge cases (like proper content-type headers) correctly, and makes your intent clear. Use it.

### A Common Gotcha: NumPy Types

ML models often return NumPy types (like `numpy.int64`) instead of plain Python types. `jsonify` can choke on these. The fix is to convert them explicitly:

```python
prediction = int(model.predict(input_df)[0])        # int() converts numpy.int64 → int
probability = float(model.predict_proba(input_df)[0][1])  # float() converts numpy.float64 → float
```

This is why, in Article 5, you saw `int(...)` and `float(...)` wrapped around the model outputs. Now you know why — it's to make them JSON-friendly.

---

## Part 7 — The Complete ML Serving Pattern

Now let's assemble everything into the standard, complete pattern for serving any ML model. This is the template you'll reuse for almost every model deployment.

```python
"""app.py — The standard Flask pattern for serving an ML model."""
from flask import Flask, request, jsonify
import joblib
import pandas as pd

# ── 1. Create the app ──────────────────────────────────
app = Flask(__name__)

# ── 2. Load the model ONCE at startup ──────────────────
# This runs once when the server starts, NOT on every request.
model = joblib.load("models/model.pkl")

# The exact feature names/order the model expects
FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]

# ── 3. Health check endpoint ───────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

# ── 4. Prediction endpoint ─────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    # a) Read the incoming JSON
    data = request.get_json()

    # b) Arrange it into the model's expected format
    input_df = pd.DataFrame([[data[f] for f in FEATURES]], columns=FEATURES)

    # c) Get the prediction (convert numpy types to Python types)
    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])

    # d) Send the result back as JSON
    return jsonify({
        "prediction": prediction,
        "probability": round(probability, 4),
        "interpretation": "Heart disease likely" if prediction == 1
                          else "Heart disease unlikely"
    })

# ── 5. Start the server ────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### The Single Most Important Design Decision: Load the Model Once

Notice that `model = joblib.load("models/model.pkl")` sits at the **top level**, outside any function. This is deliberate and critical.

- **Right way (above):** The model loads **once** when the server starts. Every prediction request reuses the already-loaded model. Fast.
- **Wrong way:** Loading the model *inside* the `predict()` function would reload it from disk on **every single request** — adding seconds of delay to each prediction and wasting memory. Never do this.

*Analogy: You hire the chef once when the restaurant opens, not freshly for every single order. Loading the model per-request is like firing and re-hiring the chef for every customer.*

### Why `host="0.0.0.0"`?

This came up in Article 5 and matters especially inside Docker:

- `app.run()` with no host defaults to `127.0.0.1` (localhost), meaning the API is only reachable from *the same machine* — or inside the same container. Nothing outside can reach it.
- `host="0.0.0.0"` tells Flask to accept requests from *any* network interface, making it reachable from outside the container or machine.

*Analogy: `127.0.0.1` is a private intercom that only works inside your own house. `0.0.0.0` is a public phone line the outside world can actually call.*

---

## Part 8 — Testing Your API

Once your Flask app is running (`python app.py`), test it. You have several options.

### Option A: curl (Command Line)

```bash
# Test the health endpoint
curl http://localhost:5000/health

# Test a prediction (send JSON with -d)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233, "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1}'
```

**Breaking down the curl command:**
- `-X POST` — use the POST method.
- `-H "Content-Type: application/json"` — tell the server we're sending JSON.
- `-d '{...}'` — the actual JSON data we're sending.

### Option B: Python (requests library)

This is how another Python program would call your API:

```python
import requests

response = requests.post(
    "http://localhost:5000/predict",
    json={
        "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233,
        "fbs": 1, "restecg": 0, "thalach": 150, "exang": 0,
        "oldpeak": 2.3, "slope": 0, "ca": 0, "thal": 1
    }
)

print(response.json())
# {'prediction': 1, 'probability': 0.78, 'interpretation': 'Heart disease likely'}
```

The `json={...}` argument automatically sends your dictionary as JSON. `response.json()` reads the JSON reply back into a Python dictionary.

### Option C: Browser (GET endpoints only)

For GET endpoints like `/health`, you can just visit `http://localhost:5000/health` in your browser. (POST endpoints can't be tested this way since browsers send GET when you type a URL.)

---

## Part 9 — Production Notes: Why `app.run()` Isn't Enough

Here's something important that beginners often miss. When you run `python app.py` and Flask starts, you may see a warning like:

```
WARNING: This is a development server. Do not use it in a production deployment.
```

Flask's built-in server (`app.run()`) is meant for **development and testing only**. It's single-threaded and not built to handle real traffic — many simultaneous users would overwhelm it.

### The Solution: A Production Server (Gunicorn)

For real deployment, you run your Flask app through a production-grade server like **Gunicorn** (Green Unicorn). Gunicorn can run multiple "workers" to handle many requests at once.

```bash
# Install it
pip install gunicorn

# Run your app with 4 worker processes
# "app:app" means: in the file app.py, use the object named 'app'
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

**Breaking it down:**
- `--workers 4` — run 4 parallel worker processes to handle concurrent requests.
- `--bind 0.0.0.0:5000` — listen on port 5000, reachable from outside.
- `app:app` — the format is `filename:flask_object_name`. Our file is `app.py` and the Flask object inside it is named `app`.

*Analogy: `app.run()` is a single waiter who can serve one table at a time — fine for practicing at home. Gunicorn is a full waitstaff that serves many tables at once — what you need when the restaurant is actually open to the public.*

### Connecting Back to Docker

In Article 5, our Dockerfile ended with `CMD ["python", "app.py"]` for simplicity. For a production ML service, you'd swap that line for Gunicorn:

```dockerfile
# Development (what we used in Article 5)
CMD ["python", "app.py"]

# Production (recommended for real deployment)
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
```

You'd also add `gunicorn` to your `requirements.txt`. Everything else in the Dockerfile stays the same. This one change takes your containerized model from "works for testing" to "ready for real traffic."

---

## Summary

You now know enough Flask to deploy any ML model:

✅ **Why models need Flask** — to turn an unusable file into a service any program can call (the waiter and service window)  
✅ **How Flask works** — the three-step pattern: create app, define routes, run server  
✅ **The request-response cycle** — the core loop every API follows  
✅ **Routes and methods** — GET for checks, POST for predictions  
✅ **Reading input** — `request.get_json()` turns incoming JSON into a Python dict  
✅ **Sending output** — `jsonify()` turns your results into a JSON response (and why to wrap numpy types in `int()`/`float()`)  
✅ **The complete serving pattern** — load the model once at startup, not per request  
✅ **Testing** — with curl, Python requests, or the browser  
✅ **Production** — why `app.run()` isn't enough and how Gunicorn fixes it  

### The Full Series, Connected

You now have every layer of taking a model to production:

| Tool | Role | Article |
|------|------|---------|
| **Git / GitHub** | Version and share code | 1, 2 |
| **DVC** | Version data and models | 3 |
| **Flask** | Wrap the model in an API | 6 (this one) |
| **Docker** | Package the API + environment | 4, 5 |

The natural flow: you write model code (versioned with **Git**), track your datasets and trained models (with **DVC**), wrap the model in an API (with **Flask**), and package the whole thing into a portable container (with **Docker**) that runs identically anywhere — served in production by **Gunicorn**.

### Where to Go Next

- **FastAPI** — a modern alternative to Flask with automatic input validation and interactive docs; increasingly popular for ML APIs
- **Pydantic** — validate incoming request data so bad input gets a clear error instead of a crash
- **Request validation & error handling** — return helpful messages when a client sends missing or malformed data
- **Batch predictions** — accept many records in one request for efficiency
- **Authentication** — protect your API with API keys or tokens before exposing it publicly

You can now take a trained model and turn it into a live, callable service — the final bridge between "I built a model" and "people can actually use my model."
