from __future__ import annotations

from dataclasses import dataclass, field

from .dfa import DFA


@dataclass(frozen=True)
class MatchStep:
    """Information about one DFA processing step."""

    index: int
    character: str
    previous_state: int
    next_state: int
    match_found: bool
    match_start: int | None


@dataclass
class DFAMatcher:
    """Runs text through a DFA one character at a time."""

    dfa: DFA
    text: str
    index: int = 0
    state: int = 0
    matches: list[int] = field(default_factory=list)

    def reset(self) -> None:
        self.index = 0
        self.state = 0
        self.matches.clear()

    @property
    def finished(self) -> bool:
        return self.index >= len(self.text)

    @property
    def processed_count(self) -> int:
        return self.index

    def step(self) -> MatchStep | None:
        if self.finished:
            return None

        character = self.text[self.index]
        previous_state = self.state
        self.state = self.dfa.next_state(self.state, character)

        match_found = self.state == self.dfa.accepting_state
        match_start: int | None = None

        if match_found:
            match_start = self.index - len(self.dfa.pattern) + 1
            self.matches.append(match_start)

        step_result = MatchStep(
            index=self.index,
            character=character,
            previous_state=previous_state,
            next_state=self.state,
            match_found=match_found,
            match_start=match_start,
        )
        self.index += 1
        return step_result

    def run_to_end(self) -> list[int]:
        while not self.finished:
            self.step()
        return list(self.matches)
