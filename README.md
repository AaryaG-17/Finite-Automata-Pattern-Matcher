# Finite Automata Pattern Matcher

An interactive desktop application for building and visualizing a deterministic finite automaton (DFA) from a pattern.

The application also accepts text input for pattern-processing workflows while keeping the DFA construction and visualization separate from the user interface.

The project is designed to be **cross-platform and device-independent**. It does not require Graphviz, a database, a compiler, a GPU, or any OS-specific library.

## Features

- Enter text to be processed.
- Enter a pattern.
- Build a deterministic finite automaton directly from the pattern.
- Display the DFA as an interactive visual state machine.
- Show the start state and accepting state.
- Show DFA transitions graphically.
- Show the complete transition table.
- Display an `OTHER` transition for characters outside the pattern alphabet.
- Zoom and pan the DFA visualization.
- Fit the complete DFA inside the visualization area.
- Built-in automated tests for DFA construction and pattern matching logic.

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
│   ├── graph_view.py
│   ├── main_window.py
│   └── matcher.py
└── tests/
    ├── __init__.py
    ├── test_dfa.py
    └── test_matcher.py