# Prerequisite P5: How the Web Works — localhost, Ports, and HTTP

*The final piece before Flask and FastAPI make complete sense: what actually happens when one program talks to another over a network*

---

## Introduction

In P1, you met the client-server model in passing — a customer placing an order, a kitchen preparing it. In Articles 6 and 7, you ran commands like `app.run(host="0.0.0.0", port=5000)` and `docker run -p 8000:5000`, and visited addresses like `http://localhost:8000/predict`. This article is where all of that finally gets explained properly, from the ground up.

By the end, you won't just *run* these commands — you'll understand exactly what's happening behind each one: what an address really means, why ports exist, what HTTP actually is, and what's literally occurring when your browser or `curl` talks to your Flask or FastAPI app. This is the last prerequisite — after this, you're fully equipped for the entire series.

---

## 📋 What This Article Covers

| # | Topic |
|---|-------|
| 1 | Networks and the internet, in plain terms |
| 2 | IP addresses — a computer's street address |
| 3 | `localhost` and `127.0.0.1` — talking to yourself |
| 4 | Ports — why one address isn't enough |
| 5 | Putting it together: the full address of a service |
| 6 | HTTP — the language of the web |
| 7 | Anatomy of a URL |
| 8 | Requests and responses, in full detail |
| 9 | JSON — the common data format |
| 10 | Seeing it all in action |
| 11 | What's really happening when you run Flask/FastAPI |
| 12 | Connecting back to Docker's port mapping |

---

## Part 1 — Networks and the Internet, in Plain Terms

A **network** is simply a group of computers connected so they can send information to each other. Your home WiFi is a small network. The **internet** is the enormous network of networks — billions of computers worldwide, all able to reach each other.

### The Postal System Analogy

Think of the internet like a global postal system. Any computer can send a "letter" (a piece of data) to any other computer, as long as it knows the correct **address**. The postal system doesn't care what's inside the envelope — a birthday card or a legal document — it just needs a valid address to deliver it. Computers work the same way: the network doesn't care if the data is a webpage, a photo, or a prediction from your ML model — it just needs a valid address to deliver it to.

This article is about understanding that address system, and the "language" computers use once the letter arrives.

---

## Part 2 — IP Addresses: A Computer's Street Address

Every computer connected to a network has an **IP address** — a unique number that identifies it, the same way every house has a unique street address.

An IP address looks like this:

```
192.168.1.42
```

Four numbers separated by dots. This is how one computer says "send your data here" to another. When you visit a website, your browser is really sending a request to the website's server's IP address (usually found automatically via a domain name, which we won't dig into here — not needed for this series).

### Analogy Recap

- **The internet** = the global postal network
- **An IP address** = a specific street address on that network

You don't need to memorize or work with raw IP addresses much in this series — but one very special IP address comes up constantly, and it deserves its own section.

---

## Part 3 — `localhost` and `127.0.0.1`: Talking to Yourself

Here's a question that confuses every beginner: when you run a Flask or FastAPI app and visit `http://localhost:8000`, who are you actually talking to?

**Answer: yourself.** Specifically, your own computer.

### The Special Address That Means "Me"

Every computer has a reserved IP address — **`127.0.0.1`** — that always means "this very computer, right here." It's a loopback address: a request sent to `127.0.0.1` never leaves your machine. It goes out and immediately comes right back to you, like a letter addressed to your own house.

**`localhost`** is just a friendly nickname for `127.0.0.1`. They mean exactly the same thing — `localhost` is simply easier for humans to type and remember.

```
http://localhost:8000        ──┐
                                ├──►  both mean the exact same thing:
http://127.0.0.1:8000        ──┘     "talk to a service running on MY OWN computer"
```

### Why This Matters for Development

When you're developing and testing your Flask/FastAPI app, you run it on your own laptop and visit it via `localhost`. Nobody else in the world can reach `localhost:8000` on *your* machine — it's strictly private to you, which makes it perfect and safe for testing before you actually deploy (recall the "deploying" concept from P1 — `localhost` is the "cooking at home" stage, not yet "opening the restaurant").

---

## Part 4 — Ports: Why One Address Isn't Enough

An IP address gets you to the right *computer*. But a single computer can run **many different services at once** — your Flask app, a database, a code editor's live preview, dozens of background programs. If a request just says "go to this computer," how does the computer know *which* of those many services it's meant for?

This is the problem **ports** solve.

### The Apartment Building Analogy

Imagine an IP address is the street address of a large **apartment building** — say, "100 Main Street." That gets mail to the right building, but the building has hundreds of units inside. You also need a **unit number** to reach the right resident.

**A port is that unit number.** It's a number (from 0 to 65535) that identifies a specific service running on a computer. "100 Main Street, Unit 8000" gets you to exactly the right place — the IP address gets you to the right computer, and the port gets you to the right *service* running on it.

```
   IP address                     Port
┌──────────────┐         ┌─────────────────┐
│ 192.168.1.42 │   +     │      8000       │   =  one specific service
│ (the building)│         │  (the unit #)   │      on one specific computer
└──────────────┘         └─────────────────┘
```

### Common Ports You'll Recognize

A handful of ports have informal conventions in development:

| Port | Commonly used for |
|------|--------------------|
| 5000 | Flask's default development port |
| 8000 | A very common alternative dev port (used by FastAPI's Uvicorn, Django, and many examples in this series) |
| 80 | Standard web traffic (HTTP) in production |
| 443 | Secure web traffic (HTTPS) in production |

There's nothing magical about these numbers — they're just widely-followed conventions. You could run your Flask app on port 9999 if you wanted; you'd just need to tell both your app and anyone connecting to it.

---

## Part 5 — Putting It Together: The Full Address of a Service

Now you can fully decode an address you've typed many times in this series:

```
http://localhost:8000
  │       │       │
  │       │       └── PORT: which service on that computer (8000)
  │       └────────── HOST: which computer (localhost = this one)
  └────────────────── PROTOCOL: the "language" being spoken (http — next section)
```

In plain English: *"Speak HTTP, to the service listening on port 8000, on my own computer."* This is precisely what your browser, `curl`, or `requests.post(...)` does every single time you've tested an API in Articles 6 and 7.

---

## Part 6 — HTTP: The Language of the Web

Knowing the address gets your message to the right doorstep. But once it arrives, both sides need to **speak the same language** so the message actually makes sense. That language, for the web, is **HTTP**.

### What HTTP Is

**HTTP** stands for **HyperText Transfer Protocol**. A "protocol" is just an agreed-upon set of rules for communicating — like a shared language with fixed grammar, so both sides understand each other perfectly.

### The Phone Call Analogy

Think about how a phone call works: there's an expected pattern. You dial a number (the address), the other person picks up and says "Hello?" (acknowledgment), you state your business, they respond, and eventually you both say goodbye and hang up. Neither side needs to invent this pattern each time — it's a shared social protocol everyone follows.

HTTP is this same idea, formalized for computers: a fixed pattern of "here's my request, in this exact format" followed by "here's my response, in this exact format," that every web browser, server, and API in the world agrees to follow. This shared agreement is *why* a Python program (`requests`), a command-line tool (`curl`), and a web browser can all talk to your FastAPI app interchangeably — they all speak the same HTTP language.

---

## Part 7 — Anatomy of a URL

You've typed dozens of URLs throughout this series. Let's break one down completely, piece by piece, using one from Article 7:

```
http://localhost:8000/predict
 │       │        │      │
 │       │        │      └── PATH: which endpoint/resource (recall "endpoints" from Article 7)
 │       │        └───────── PORT: which service
 │       └────────────────── HOST: which computer
 └────────────────────────── PROTOCOL: which language (HTTP)
```

A URL (Uniform Resource Locator) is simply a complete, structured address: protocol + host + port + path. Sometimes a URL also has a **query string** — extra parameters tacked onto the end, after a `?`:

```
http://localhost:8000/search?term=heart&limit=10
                              └──────┬──────────┘
                                query string: extra parameters
                                term=heart, limit=10
```

You won't use query strings much in this series (our APIs mostly take input as JSON in the request body, as you saw in Articles 6–7), but recognizing them when you see them elsewhere is useful.

---

## Part 8 — Requests and Responses, in Full Detail

You met the request-response cycle conceptually in P1 and Article 7. Now let's look at the actual anatomy of each side in full, technical detail — this is exactly what's flowing back and forth every time you call your ML API.

### The Request (What the Client Sends)

```
POST /predict HTTP/1.1                          ← 1. Method + Path + Protocol version
Host: localhost:8000                             ← 2. Headers (metadata)
Content-Type: application/json
{                                                 ← 3. Body (the actual data)
  "age": 63, "sex": 1, "chol": 233
}
```

**1. The method and path** — what action, on what resource. `POST /predict` means "send data to the `/predict` endpoint."

**2. Headers** — metadata *about* the request, not the data itself. `Content-Type: application/json` is the client saying "heads up, the body below is in JSON format." Think of headers as the information on the outside of an envelope — sender, format, special handling instructions — separate from the letter inside.

**3. The body** — the actual payload, the patient data being sent for prediction. GET requests (simple "give me something" calls, like `/health`) usually have no body, since there's nothing to send — only POST requests (which deliver data) typically include one.

### The Response (What the Server Sends Back)

```
HTTP/1.1 200 OK                                   ← 1. Protocol version + Status code
Content-Type: application/json                    ← 2. Headers
{                                                  ← 3. Body (the result)
  "prediction": 1, "probability": 0.78
}
```

**1. The status code** — a number summarizing what happened. You met these in Article 7: `200` (success), `422` (your input was invalid), `404` (that endpoint doesn't exist), `500` (the server crashed). It's the very first thing worth checking when something goes wrong — it tells you broadly *which side* the problem is on.

**2. Headers** — again, metadata about the response, like its content type.

**3. The body** — the actual result: your model's prediction, sent back as JSON.

### Why This Matters Practically

When you wrote `request.get_json()` in Flask (Article 6) or used a Pydantic model in FastAPI (Article 7), you were reading the **body** of an incoming request. When you wrote `jsonify({...})` or `return PredictionResponse(...)`, you were building the **body** of the outgoing response. Now you know exactly which part of the request-response anatomy that code was touching.

---

## Part 9 — JSON: The Common Data Format

You've seen JSON in every API article so far. Let's understand precisely why it's used.

### The Problem JSON Solves

A request body needs to carry structured data — multiple named values, like a patient's age, cholesterol, and so on — across the network, between programs that might be written in completely different languages (Python, JavaScript, Java...). They need a shared, language-neutral way to represent that structure.

### JSON: A Universal Format

**JSON** (JavaScript Object Notation, despite the name, used by virtually every language) represents data as labeled key-value pairs, very close to how a Python dictionary looks:

```json
{
  "age": 63,
  "sex": 1,
  "chol": 233
}
```

```python
# The Python dictionary equivalent — nearly identical
{
    "age": 63,
    "sex": 1,
    "chol": 233
}
```

This near-identical structure is exactly why `request.get_json()` in Flask hands you back a regular Python dictionary, and why FastAPI's Pydantic models convert so cleanly between JSON and Python objects (Article 7). JSON is the *universal* shipping format; Python dictionaries are how that data looks once it's unpacked inside your code.

*Analogy: JSON is like a standardized international shipping label format. Any country's customs office (any programming language) can read it, regardless of what language is spoken locally — because the label's structure is universally agreed upon.*

---

## Part 10 — Seeing It All in Action

Let's make all of this concrete with hands-on observation, using tools you already know from P2.

### Using `curl` to See Raw Responses

```bash
curl -i http://localhost:8000/health
```

The `-i` flag (include headers) shows you the **full response**, including the parts normally hidden:

```
HTTP/1.1 200 OK                          ← status line
content-type: application/json           ← header
content-length: 22

{"status":"healthy"}                     ← body
```

Now you can see, in raw form, exactly the anatomy described in Part 8 — the status code, the headers, and the body, laid bare.

### Using Your Browser's Developer Tools

Open any website, right-click → **Inspect** → go to the **Network** tab, then reload the page. You'll see a live list of every single request your browser made — each with its method, status code, and timing. This is the exact request-response cycle from Part 8, happening dozens of times per page load, now visible to you.

---

## Part 11 — What's Really Happening When You Run Flask/FastAPI

Now, the payoff. Let's revisit code from Articles 6 and 7 and fully decode it with everything you now know.

### Flask

```python
app.run(host="0.0.0.0", port=5000)
```

In full plain English: *"Start listening for HTTP requests on port 5000. Accept connections from any host (`0.0.0.0`), not just `localhost` — meaning other computers on the network can reach this too, not only this machine."*

Recall from Part 4: had you used the default (`127.0.0.1`/`localhost`), only requests *originating from this same computer* could reach your app — useful for local testing, but invisible to anyone else, including from inside a Docker container trying to reach out (Article 5 explained this practically; now you understand *why*, from first principles).

### FastAPI / Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Same idea, same reasoning: *"Run my FastAPI app (`main:app`), accept requests addressed to port 8000, from any host able to reach this machine."*

### A Request Arriving, Step by Step

When you run `curl -X POST http://localhost:8000/predict -d '{...}'` (as in Article 7), here's the complete, now-fully-understood journey:

```
1. curl resolves "localhost" → 127.0.0.1 (Part 3: talking to yourself)
2. curl connects to port 8000 on that address (Part 4: the right service)
3. curl speaks HTTP: sends a POST request to path /predict,
   with a JSON body (Parts 6–9: the language and format)
4. FastAPI, listening on that exact host+port, receives the request
5. FastAPI matches the path "/predict" to your function (Article 7's routing)
6. Pydantic validates the JSON body against your schema (Article 7)
7. Your function runs, gets a prediction
8. FastAPI builds an HTTP response: status 200, JSON body with the result
9. curl receives the response and prints the body to your terminal
```

Every step of this was once invisible magic. Now it's a sequence of concrete, nameable ideas you understand individually.

---

## Part 12 — Connecting Back to Docker's Port Mapping

One last piece falls into place: the `-p` flag from `docker run`, first seen in Article 5.

```bash
docker run -d -p 8000:5000 --name heart-api heart-disease-api:v1
```

Recall from Article 4: a container is an isolated environment — its own little world, with its own internal `localhost`. When your Flask app inside the container listens on port 5000, it's listening on *the container's own* `127.0.0.1` — invisible from outside, exactly like the loopback concept from Part 3, just one level deeper (your laptop, containing a container, containing an app).

`-p 8000:5000` builds a bridge between two separate "loopback worlds":

```
   YOUR LAPTOP                          CONTAINER (its own isolated world)
┌─────────────────────┐              ┌──────────────────────────────┐
│  localhost:8000      │  -p 8000:5000 │  localhost:5000 (inside)     │
│  (you visit this)    │ ───────────► │  Flask app listening here    │
└─────────────────────┘   forwards   └──────────────────────────────┘
```

Now this line of the Dockerfile from Article 5 is fully transparent: `EXPOSE 5000` only *documents* that the app listens on port 5000 inside the container (Part 4's "service unit number," but inside an isolated world); `-p 8000:5000` at `docker run` time is what actually builds the bridge from your laptop's port 8000 to the container's port 5000 — without it, the container's internal `localhost:5000` would remain exactly as unreachable from outside as your own `localhost` is to other people, per Part 3.

---

## Summary

You now understand the complete machinery behind every web request in this series:

✅ **Networks and IP addresses** — computers reaching each other via unique addresses, like the postal system  
✅ **`localhost` / `127.0.0.1`** — the special address that always means "this very computer"  
✅ **Ports** — the "unit number" that picks a specific service out of many running on one computer  
✅ **Full addresses** — protocol + host + port + path, fully decoded  
✅ **HTTP** — the shared "language" that lets any client and any server understand each other  
✅ **URL anatomy** — protocol, host, port, path, and query strings  
✅ **Requests and responses** — method, headers, body on the request; status code, headers, body on the response  
✅ **JSON** — the universal, language-neutral format for structured data, and why it maps so cleanly to Python dictionaries  
✅ **`host="0.0.0.0"`** — fully understood, not just copied  
✅ **Docker's `-p` flag** — the bridge between your laptop's loopback world and a container's isolated loopback world  

You now have every prerequisite this series assumes. Nothing from here forward should feel like an unexplained incantation — every command, every address, every line of Flask or FastAPI code is something you can read and reason about from first principles.

### The Prerequisite Series, Complete

| Article | What it built |
|---------|---------------|
| **P1** | The mental model — code, programs, deployment, client-server |
| **P2** | The terminal — navigating and running things by typing |
| **P3** | Your toolkit — VS Code, Python, and Git, installed and working together |
| **P4** | Python environments — `pip`, `venv`, `requirements.txt` |
| **P5** | The web — `localhost`, ports, HTTP, and how it all connects to Flask/FastAPI/Docker |

### What's Next

You're now fully equipped to begin (or revisit) the main series from **Article 1: Git & GitHub** with complete confidence. Every terminal command, every file, every `requirements.txt`, every `localhost:8000`, and every Dockerfile line will read as understood mechanics rather than memorized magic. Welcome to development — you're ready.
