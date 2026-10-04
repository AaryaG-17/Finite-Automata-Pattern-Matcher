import unittest

from src.dfa import DFA, OTHER_SYMBOL


class TestDFA(unittest.TestCase):
    def test_basic_transitions_for_aba(self) -> None:
        dfa = DFA.build("aba")

        self.assertEqual(dfa.state_count, 4)
        self.assertEqual(dfa.accepting_state, 3)

        self.assertEqual(dfa.next_state(0, "a"), 1)
        self.assertEqual(dfa.next_state(0, "b"), 0)

        self.assertEqual(dfa.next_state(1, "a"), 1)
        self.assertEqual(dfa.next_state(1, "b"), 2)

        self.assertEqual(dfa.next_state(2, "a"), 3)
        self.assertEqual(dfa.next_state(2, "b"), 0)

        # From the accepting state, "a" preserves the overlap for "aba".
        self.assertEqual(dfa.next_state(3, "a"), 1)
        self.assertEqual(dfa.next_state(3, "b"), 2)

    def test_other_character_returns_to_q0(self) -> None:
        dfa = DFA.build("abc")
        self.assertEqual(dfa.next_state(2, "x"), 0)
        self.assertEqual(dfa.next_state(3, "!"), 0)
        self.assertEqual(dfa.transitions[0][OTHER_SYMBOL], 0)

    def test_repeated_pattern(self) -> None:
        dfa = DFA.build("aaa")
        self.assertEqual(dfa.next_state(0, "a"), 1)
        self.assertEqual(dfa.next_state(1, "a"), 2)
        self.assertEqual(dfa.next_state(2, "a"), 3)
        self.assertEqual(dfa.next_state(3, "a"), 3)

    def test_empty_pattern_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DFA.build("")


if __name__ == "__main__":
    unittest.main()
