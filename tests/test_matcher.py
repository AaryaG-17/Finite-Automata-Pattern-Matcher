import unittest

from src.dfa import DFA
from src.matcher import find_matches


class TestMatcher(unittest.TestCase):

    def test_single_match(self):
        dfa = DFA.build("cats")

        self.assertEqual(
            find_matches("I like cats.", dfa),
            [7],
        )

    def test_multiple_matches(self):
        dfa = DFA.build("cats")

        self.assertEqual(
            find_matches(
                "cats are cute. I like cats.",
                dfa,
            ),
            [0, 22],
        )

    def test_overlapping_matches(self):
        dfa = DFA.build("aba")

        self.assertEqual(
            find_matches("ababa", dfa),
            [0, 2],
        )

    def test_no_match(self):
        dfa = DFA.build("hello")

        self.assertEqual(
            find_matches("goodbye", dfa),
            [],
        )

    def test_empty_text(self):
        dfa = DFA.build("abc")

        self.assertEqual(
            find_matches("", dfa),
            [],
        )

    def test_other_characters(self):
        dfa = DFA.build("abc")

        self.assertEqual(
            find_matches("xyzabc", dfa),
            [3],
        )


if __name__ == "__main__":
    unittest.main()