Finite Automata Pattern Matcher
A simple DFA constructor and visualizer built with Python and PySide6.
The application takes a pattern, constructs its Deterministic Finite Automaton (DFA), and displays:
- DFA state diagram
- Transition table
- Accepting state
- OTHER transitions
The entered text is displayed in the interface but is not processed.
Features
- DFA construction from a pattern
- Visual DFA graph
- Transition table
- Zoom and fit controls
- Dark-themed GUI
- Cross-platform
Requirements
- Python 3.10+
- PySide6
Installation
Windows
git clone https://github.com/AaryaG-17/Finite-Automata-Pattern-Matcher.git
cd Finite-Automata-Pattern-Matcher
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py

Linux / macOS
git clone https://github.com/AaryaG-17/Finite-Automata-Pattern-Matcher.git
cd Finite-Automata-Pattern-Matcher
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py

Tests
python -m unittest discover -s tests

Project Structure
Finite-Automata-Pattern-Matcher/
├── main.py
├── requirements.txt
├── src/
│   ├── dfa.py
│   ├── graph_view.py
│   └── main_window.py
└── tests/
    └── test_dfa.py

How It Works
Pattern
   ↓
DFA Construction
   ↓
DFA Graph + Transition Table

Built for learning and visualizing Deterministic Finite Automata.