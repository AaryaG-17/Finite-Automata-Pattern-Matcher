# Finite Automata-Based Pattern Matching System

A Python and PySide6 application that constructs a **Deterministic Finite Automaton (DFA)** from a pattern and uses it to find occurrences of that pattern in an input text.

## Features

- DFA construction from a given pattern
- Visual DFA state diagram
- DFA transition table
- Pattern matching using the constructed DFA
- Detection of multiple and overlapping matches
- Cross-platform GUI

## How It Works

```text
Input Text + Pattern
        ↓
   DFA Construction
        ↓
     DFA Processing
        ↓
   Matching Positions
```

The application also visualizes the constructed DFA and its transition table.

## AI Assistance & Iterative Development

AI assistance was used during development for **code generation, debugging, refactoring, documentation, and problem-solving**.

The project was developed iteratively through repeated cycles of implementation, testing, debugging, review, and refinement.

## Requirements

- Python 3.10+
- PySide6
- Git

## Setup

### Common Commands

```bash
git clone https://github.com/AaryaG-17/Finite-Automata-Pattern-Matcher.git
cd Finite-Automata-Pattern-Matcher
pip install -r requirements.txt
python main.py
```

### Windows

Create and activate the virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Then run the **Common Commands** above.

### Linux / macOS

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then run the **Common Commands** above.

### Run Tests

```bash
python -m unittest discover -s tests
```

## Project Structure

```text
Finite-Automata-Pattern-Matcher/
├── main.py
├── requirements.txt
├── src/
│   ├── dfa.py
│   ├── graph_view.py
│   ├── main_window.py
│   └── matcher.py
└── tests/
    ├── test_dfa.py
    └── test_matcher.py
```

## Example

**Text:**

```text
ababa
```

**Pattern:**

```text
aba
```

**Result:**

```text
Pattern found at positions 0, 2
```

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub!
