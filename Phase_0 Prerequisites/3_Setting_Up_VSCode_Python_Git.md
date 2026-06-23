# Prerequisite P3: Setting Up Your Computer - VS Code, Python, and Git

*Installing and actually using the three tools every article in this series assumes you already have*

---

## Introduction

In P1 you built the mental model. In P2 you learned to talk to your computer through the terminal. Now it's time to install the actual toolkit: **VS Code** (where you'll write code), **Python** (the language that runs it), and **Git** (which you'll use from Article 1 onward).

Every single hands-on article in this series assumes these three things are already sitting on your computer, ready to go. This article gets you there - properly installed, verified, and comfortable enough to use day to day. We won't just install things; we'll tour each tool so you know what you're looking at.

---

## 📋 What This Article Covers

| # | Topic |
|---|-------|
| 1 | Why a code editor? Introducing VS Code |
| 2 | Installing VS Code |
| 3 | A guided tour of the VS Code interface |
| 4 | The integrated terminal (your new home base) |
| 5 | Installing Python |
| 6 | Verifying Python and understanding `python` vs `pip` |
| 7 | Installing Git |
| 8 | Verifying Git and first-time configuration |
| 9 | Useful VS Code extensions for this series |
| 10 | Putting it together: your first project folder |

---

## Part 1 - Why a Code Editor? Introducing VS Code

In P1, you learned that code is just text with instructions saved in a file. So technically, you could write code in Notepad or any plain text app. So why does every developer use something fancier?

### The Workshop Analogy

Writing code in a plain text editor is like building furniture with your bare hands, technically possible, painfully slow. A **code editor** is a fully equipped workshop: it has the right tools laid out, it catches your mistakes before they become real problems, and it shows you what you're doing as you do it.

**VS Code** (Visual Studio Code, made by Microsoft, free and open-source) is the most widely used code editor in the world today. It's not the only option, but it's an excellent, beginner-friendly default which is why this series assumes you're using it.

### What a Code Editor Actually Gives You

| Plain text editor | Code editor (VS Code) |
|--------------------|------------------------|
| Plain black text | Color-coded text by meaning (**syntax highlighting**) |
| No error checking | Underlines mistakes before you run anything |
| Separate terminal window | A terminal built right in |
| No project view | A file explorer showing your whole project |
| No help while typing | Auto-suggestions as you type (**autocomplete**) |

The biggest win for beginners: VS Code **shows you problems before you run your code**, the same way a word processor underlines a misspelled word before you hit print.

---

## Part 2 - Installing VS Code

### Step 1: Download

Go to **https://code.visualstudio.com** in your browser. The site automatically detects your operating system and shows a big **Download** button. Click it.

### Step 2: Install

**On Windows:**
- Open the downloaded `.exe` file.
- Click through the installer (default options are fine).
- ✅ Important: when you reach the "Select Additional Tasks" screen, make sure **"Add to PATH"** is checked. This lets you open VS Code by typing `code` in the terminal — a feature you'll use constantly.

**On macOS:**
- Open the downloaded `.zip` file, it extracts a `Visual Studio Code` app.
- Drag it into your **Applications** folder.
- Open it once from Applications. Then, inside VS Code, press `Cmd+Shift+P`, type "shell command," and select **"Shell Command: Install 'code' command in PATH."** This enables the `code` command in your terminal, same as Windows above.

**On Linux:**
- Download the `.deb` (Ubuntu/Debian) or `.rpm` (Fedora) package and install it, or use your package manager:
```bash
sudo apt install ./code_*.deb
```

### Step 3: Verify

Open your terminal (from P2) and type:

```bash
code --version
```

If you see a version number, VS Code is installed and the terminal can launch it. If you get "command not found," revisit the PATH step above for your OS.

A handy trick you'll use constantly: from inside any folder in your terminal, typing `code .` opens that entire folder in VS Code (`.` meaning "here," as you learned in P2).

```bash
cd my_project
code .
```

---

## Part 3 - A Guided Tour of the VS Code Interface

Open VS Code. Here's what you're looking at, region by region.

```
┌─────────────────────────────────────────────────────────────┐
│  ☰  File  Edit  View  ...                    (menu bar)       │
├────┬────────────────────────────────────────────────────────┤
│    │  EXPLORER                                               │
│ A  │  ▾ heart_disease_project          ← your project folder │
│ C  │    ▸ data                                                │
│ T  │    ▾ src                                                 │
│ I  │      train.py                     ← click to open       │
│ V  │      app.py                       ┌───────────────────┐ │
│ I  │    README.md                      │  train.py    ✕    │ │
│ T  │                                   ├───────────────────┤ │
│ Y  │  (sidebar: Explorer,              │ 1  import pandas  │ │
│    │   Search, Git, Extensions...)     │ 2  ...            │ │
│ B  │                                   │  (your code here, │ │
│ A  │                                   │   color-coded)    │ │
│ R  │                                   └───────────────────┘ │
├────┴────────────────────────────────────────────────────────┤
│  >_  TERMINAL                                                │
│  $                              ← your built-in terminal      │
└─────────────────────────────────────────────────────────────┘
```

### The Four Regions

**1. Activity Bar (far left, icons)**
Switches between major views: the file Explorer, Search, Source Control (Git — you'll use this heavily from Article 1), and Extensions.

**2. Explorer (sidebar)**
Shows your project's files and folders, exactly like the `ls` command from P2, but visual and clickable. Click any file to open it.

**3. Editor (center, the big area)**
Where you actually read and write code. Multiple files open as tabs across the top, just like browser tabs.

**4. Terminal (bottom panel)**
A real terminal, the exact same thing you used in P2, built directly into your editor. This is the single biggest reason VS Code suits this series: you write code and run terminal commands in one window, without switching apps.

### Opening a Project

Use **File → Open Folder...** (or `code .` from the terminal, as shown above) to open an entire project folder. VS Code always works best when you open the *folder*, not individual files — this is what makes the Explorer sidebar and Git integration work properly.

---

## Part 4 - The Integrated Terminal (Your New Home Base)

This is where P2's skills and VS Code merge into your daily workflow.

### Opening the Terminal

- Menu: **Terminal → New Terminal**
- Or the keyboard shortcut: `` Ctrl+` `` (Windows/Linux) or `` Cmd+` `` (Mac) — the backtick key, usually above Tab.

A terminal panel appears at the bottom, **already standing inside your currently open project folder.** This is a small but huge convenience — no `cd`-ing around to find your project; VS Code starts you right there.

### Why This Matters for Every Article in This Series

From this point on, your workflow in every article looks like this:

```
┌─────────────────────────────────────────────┐
│  1. Edit code in the Editor (top)            │
│  2. Run commands in the Terminal (bottom)    │
│  3. See results, go back to step 1           │
└─────────────────────────────────────────────┘
```

You'll write `train.py` in the editor, then type `python train.py` in the terminal below it, all without leaving VS Code. Later, you'll type `git commit`, `docker build`, `dvc add` in this exact same terminal. One window, your whole workflow.

### A Quick Practice

Try this now — open the terminal in VS Code and run the safe, read-only commands from P2:

```bash
pwd
ls
```

You should see you're already inside the folder you opened in VS Code. That's the integration working for you.

---

## Part 5 - Installing Python

Python is the language behind every code example in this series. Let's get it installed.

### Step 1: Download

Go to **https://www.python.org/downloads/**. Click the big "Download Python 3.x.x" button (get the latest stable version).

### Step 2: Install

**On Windows:**
- Run the installer.
- ✅ **Critical step:** On the very first screen, check the box **"Add python.exe to PATH"** at the bottom before clicking Install. This is the single most common setup mistake — missing this means typing `python` later won't work.
- Click "Install Now."

**On macOS:**
- Run the downloaded `.pkg` installer and click through it (defaults are fine).
- *Note:* macOS often ships with an old built-in Python 2 for internal system use — never touch or rely on this. Always use the Python 3 you just installed.

**On Linux:**
- Most distributions include Python 3 already. Confirm with the command below; if missing, install with `sudo apt install python3` (Ubuntu/Debian).

### Step 3: Verify

Open (or reopen) your terminal — in VS Code or standalone — and run:

```bash
python --version
```

You should see something like `Python 3.11.5`. 

> **If `python` isn't recognized but `python3` is:** Some systems (especially Mac/Linux) use the command `python3` instead of `python`. Try `python3 --version`. Throughout this series, if `python` doesn't work, substitute `python3` everywhere — they refer to the same install.

---

## Part 6 - Verifying Python and Understanding `python` vs `pip`

Now that Python is installed, you actually have **two** related commands available. Telling them apart clears up a lot of early confusion.

### `python` - Runs Code

As you saw in P1 and P2, `python` *executes* a file of instructions:

```bash
python train.py
```

### `pip` - Installs Extra Tools (Packages)

Python comes with a lot built in, but ML work needs extra **packages** which are pre-written code libraries like `pandas` or `scikit-learn` that you didn't write yourself. `pip` is Python's package installer; it downloads and sets these up for you.

```bash
pip --version
```

```bash
# Example: installing a package (you'll do this constantly from Article 3 onward)
pip install pandas
```

*Analogy: If `python` is the chef cooking with what's in the kitchen, `pip` is the delivery service that brings in specialty ingredients you don't have yet. You'll meet `pip` properly, including `requirements.txt`, in the next prerequisite article (P4).*

### Quick Sanity Check

Try this tiny end-to-end test to confirm everything (VS Code, Python, the terminal) works together:

1. In VS Code, create a new file: `hello.py`
2. Type one line:
   ```python
   print("My setup works!")
   ```
3. Save it (`Ctrl+S` / `Cmd+S`).
4. In the VS Code terminal, run:
   ```bash
   python hello.py
   ```
5. You should see: `My setup works!`

If you see that message, your editor, your terminal, and Python are all correctly wired together. This is the exact loop -> write, save, run.

---

## Part 7 - Installing Git

Git powers Articles 1, 2, and 3, and is referenced throughout the rest of the series. Let's install it now so it's ready when you need it.

### Step 1: Download

Go to **https://git-scm.com/downloads**. It detects your OS automatically.

### Step 2: Install

**On Windows:**
- Run the installer. The default options are sensible for beginners — you can click "Next" through most screens.
- ✅ One screen asks about the default editor Git uses for commit messages — selecting **VS Code** here (if offered) is a convenient choice.
- This installer also includes **Git Bash**, a terminal that behaves like Mac/Linux — useful if you want every command in this series to match exactly, regardless of being on Windows.

**On macOS:**
- Git often comes pre-installed. Check first (Step 3 below). If missing, installing **Xcode Command Line Tools** brings it in:
  ```bash
  xcode-select --install
  ```
- Alternatively: `brew install git` if you use Homebrew.

**On Linux:**
```bash
sudo apt update
sudo apt install git
```

### Step 3: Verify

```bash
git --version
```

You should see something like `git version 2.43.0`.

---

## Part 8 - First-Time Git Configuration

Git needs to know who you are before you make your first commit (this is covered in depth in Article 1, but let's set it up now so it's ready).

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**What's happening here:** every change you save with Git gets labeled with this name and email, like signing your work. The `--global` flag means "remember this for every project on this computer," so you only do this once per machine, not per project.

Confirm it took effect:

```bash
git config --list
```

You'll see your name and email listed among Git's settings. You're now fully set up to follow Article 1 from the very first command.

---

## Part 9 - Useful VS Code Extensions for This Series

VS Code can be enhanced with **extensions** — small add-ons that give it new abilities, similar to apps on a phone. Click the **Extensions** icon in the Activity Bar (the four-squares icon) and search for these:

| Extension | What it does | Why it helps this series |
|-----------|---------------|--------------------------|
| **Python** (by Microsoft) | Adds Python-aware features: error checking, autocomplete, formatting | Essential for every code-writing article |
| **Docker** (by Microsoft) | Lets you view and manage images/containers visually, and highlights Dockerfile syntax | Helpful for Articles 4–5 |
| **GitLens** | Adds rich detail to Git history right in the editor | Optional, but great once you're comfortable with Git basics from Article 1 |

To install one: click its name in the search results, then click **Install**. 

> You don't need any of these to follow the series as everything works from the terminal alone, exactly as written in every article. Extensions just make the experience smoother once you're comfortable with the basics.

---

## Part 10 - Putting It Together: Your First Project Folder

Let's combine everything from P1 through P3 into one real, hands-on sequence — creating a small project folder the way you will for every article going forward.

```bash
# 1. Navigate to where you keep your projects (P2 skill)
cd ~
mkdir learning_projects
cd learning_projects

# 2. Create today's project folder
mkdir my_first_project
cd my_first_project

# 3. Open it in VS Code (P3 skill)
code .
```

VS Code opens with `my_first_project` as your workspace which will be empty for now. In the VS Code terminal (`` Ctrl+` ``):

```bash
# 4. Confirm your tools are all ready (P3 skill)
python --version
git --version
code --version
```

Now create a small file directly in VS Code:

1. Right-click the empty Explorer panel → **New File** → name it `welcome.py`
2. Type:
   ```python
   print("Ready for the MLOps series!")
   ```
3. Save, then in the terminal:
   ```bash
   python welcome.py
   ```

You should see `Ready for the MLOps series!` printed. At this point, you have navigated folders, opened a project in an editor, written a code file, and executed it — the complete loop every article in this series relies on.

---

