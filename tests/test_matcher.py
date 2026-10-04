import unittest

from src.dfa import DFA
from src.matcher import DFAMatcher


class TestDFAMatcher(unittest.TestCase):
    def test_finds_overlapping_occurrences(self) -> None:
        matcher = DFAMatcher(DFA.build("aba"), "ababa")
        self.assertEqual(matcher.run_to_end(), [0, 2])

    def test_finds_repeated_overlapping_occurrences(self) -> None:
        matcher = DFAMatcher(DFA.build("aaa"), "aaaaa")
        self.assertEqual(matcher.run_to_end(), [0, 1, 2])

    def test_no_match(self) -> None:
        matcher = DFAMatcher(DFA.build("xyz"), "abababab")
        self.assertEqual(matcher.run_to_end(), [])

    def test_step_information(self) -> None:
        matcher = DFAMatcher(DFA.build("ab"), "zab")

        first = matcher.step()
        self.assertIsNotNone(first)
        assert first is not None
        self.assertEqual(first.index, 0)
        self.assertEqual(first.character, "z")
        self.assertEqual(first.previous_state, 0)
        self.assertEqual(first.next_state, 0)
        self.assertFalse(first.match_found)

        matcher.step()
        result = matcher.step()
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.index, 2)
        self.assertTrue(result.match_found)
        self.assertEqual(result.match_start, 1)

    def test_empty_text(self) -> None:
        matcher = DFAMatcher(DFA.build("abc"), "")
        self.assertTrue(matcher.finished)
        self.assertIsNone(matcher.step())
        self.assertEqual(matcher.run_to_end(), [])


if __name__ == "__main__":
    unittest.main()
