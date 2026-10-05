from __future__ import annotations

from .dfa import DFA


def find_matches(text: str, dfa: DFA) -> list[int]:
    """
    Process the text using the DFA and return the starting
    positions of every occurrence of the pattern.

    Overlapping matches are included.
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    if not isinstance(dfa, DFA):
        raise TypeError("dfa must be a DFA instance.")

    matches: list[int] = []
    state = 0
    pattern_length = len(dfa.pattern)

    for index, character in enumerate(text):
        state = dfa.next_state(state, character)

        if state == dfa.accepting_state:
            matches.append(index - pattern_length + 1)

    return matches