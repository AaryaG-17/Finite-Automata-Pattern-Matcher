from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


OTHER_SYMBOL = "OTHER"


@dataclass(frozen=True)
class DFA:
    """A deterministic finite automaton specialized for exact pattern matching."""

    pattern: str
    alphabet: tuple[str, ...]
    transitions: tuple[dict[str, int], ...]
    accepting_state: int

    @staticmethod
    def _prefix_function(pattern: str) -> List[int]:
        pi = [0] * len(pattern)
        j = 0
        for i in range(1, len(pattern)):
            while j > 0 and pattern[i] != pattern[j]:
                j = pi[j - 1]
            if pattern[i] == pattern[j]:
                j += 1
            pi[i] = j
        return pi

    @classmethod
    def build(cls, pattern: str) -> "DFA":
        if not isinstance(pattern, str):
            raise TypeError("pattern must be a string")
        if not pattern:
            raise ValueError("pattern must not be empty")

        # Preserve first-occurrence order to keep the GUI readable.
        seen: set[str] = set()
        alphabet_list: list[str] = []
        for char in pattern:
            if char not in seen:
                seen.add(char)
                alphabet_list.append(char)

        alphabet = tuple(alphabet_list)
        pi = cls._prefix_function(pattern)
        m = len(pattern)
        transitions: list[dict[str, int]] = []

        # State q means the first q pattern characters currently match.
        for state in range(m + 1):
            row: dict[str, int] = {}
            for symbol in alphabet:
                candidate = state

                while candidate > 0 and (
                    candidate == m or pattern[candidate] != symbol
                ):
                    candidate = pi[candidate - 1]

                if candidate < m and pattern[candidate] == symbol:
                    candidate += 1

                row[symbol] = candidate

            # Every character outside the pattern alphabet breaks the
            # currently matched prefix and therefore returns to q0.
            row[OTHER_SYMBOL] = 0
            transitions.append(row)

        return cls(
            pattern=pattern,
            alphabet=alphabet,
            transitions=tuple(transitions),
            accepting_state=m,
        )

    @property
    def state_count(self) -> int:
        return self.accepting_state + 1

    def next_state(self, state: int, symbol: str) -> int:
        if state < 0 or state > self.accepting_state:
            raise ValueError(f"invalid DFA state: {state}")
        return self.transitions[state].get(symbol, 0)

    def transition_row(self, state: int) -> Dict[str, int]:
        if state < 0 or state > self.accepting_state:
            raise ValueError(f"invalid DFA state: {state}")
        return dict(self.transitions[state])

    def transition_symbols(self) -> tuple[str, ...]:
        return (*self.alphabet, OTHER_SYMBOL)

    def as_table(self) -> list[list[int | str]]:
        symbols = self.transition_symbols()
        table: list[list[int | str]] = []
        for state in range(self.state_count):
            row: list[int | str] = [f"q{state}"]
            row.extend(self.transitions[state][symbol] for symbol in symbols)
            table.append(row)
        return table
