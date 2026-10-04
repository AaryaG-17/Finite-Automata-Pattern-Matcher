# Finite Automata Pattern Matcher

An interactive desktop application that builds a deterministic finite automaton (DFA) from a pattern and uses that DFA to find every occurrence of the pattern inside a text.

The project is designed to be **cross-platform and device-independent**. It does not require Graphviz, a database, a compiler, a GPU, or any OS-specific library.

## Features

- Build a DFA directly from the entered pattern.
- Display the DFA as a visual state machine.
- Show accepting state(s) and start state.
- Show the complete transition table for the pattern alphabet plus an `OTHER` transition.
- Match a pattern against text using the DFA itself.
- Detect overlapping matches.
- Step through matching one character at a time.
- Run/pause an animated matching pass.
- Highlight the current input character, current DFA state, and active transition.
- Show all match positions using zero-based indexing.
- Built-in automated tests for the DFA and matcher.

## Project structure

```text
Finite-Automata-Pattern-Matcher/
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
├── src/
│   ├── __init__.py
│   ├── dfa.py
│   ├── matcher.py
│   ├── graph_view.py
│   └── main_window.py
└── tests/
    ├── __init__.py
    ├── test_dfa.py
    └── test_matcher.py
```

## Requirements

- Python 3.10 or newer
- `pip`
- A desktop environment supported by Qt (Windows, Linux, or macOS)
- The Python dependency listed in `requirements.txt`

No internet connection is needed while the application is running.

## Installation

The project uses a Python virtual environment.

### Windows — Command Prompt

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

### Windows — PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

If your Linux/macOS installation exposes Python as `python` rather than `python3`, use `python` in the commands above.

## Running tests

Activate the virtual environment first, then run:

```bash
python -m unittest discover -s tests -v
```

The tests only depend on the Python standard library and do not open the GUI.

## How the DFA works

For a pattern of length `m`, the DFA has states:

```text
q0, q1, q2, ..., qm
```

State `qi` means that the first `i` characters of the pattern currently match the suffix of the text seen so far.

For each state and each character in the pattern alphabet, the transition function chooses the largest prefix of the pattern that is also a suffix after reading that character.

The final state `qm` is accepting.

For example, for pattern `aba`:

```text
q0 --a--> q1 --b--> q2 --a--> q3
```

The accepting state is `q3`.

The DFA does not reset to `q0` after a match. Its normal transition function continues, which is what allows overlapping occurrences to be found.

For example:

```text
Text:    ababa
Pattern: aba
Matches: 0, 2
```

## `OTHER` transition

The graph and transition table show the pattern's distinct characters plus one conceptual symbol named `OTHER`.

`OTHER` means any input character that is not part of the pattern alphabet. Such a character sends the machine to `q0`.

This gives the program a practical finite representation while matching arbitrary Unicode text.

## Matching procedure

For each character in the text:

1. Read the current DFA state.
2. Read the input character.
3. Follow the corresponding DFA transition.
4. If the resulting state is accepting, record the start position of the match.
5. Continue scanning.

A match ending at text index `i` has start index:

```text
i - pattern_length + 1
```

## Design goals

The implementation deliberately keeps the automata logic separate from the GUI:

```text
GUI
 │
 ├── DFA graph
 ├── Transition table
 └── Matching animation
       │
       ▼
  DFA / Matcher engine
       │
       ▼
  Pure Python logic
```

This makes the project easier to test, explain in a viva, and reuse in another interface.

## Notes

- Matching is case-sensitive.
- Unicode text is supported because the implementation operates on Python strings.
- The visual graph is generated internally with PySide6; no external graphing application is required.
