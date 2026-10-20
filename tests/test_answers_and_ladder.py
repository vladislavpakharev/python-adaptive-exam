import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import answers  # noqa: E402
import ladder  # noqa: E402

ONE = {"id": 1, "level": 1, "type": "один", "answer": "2"}
MANY = {"id": 2, "level": 2, "type": "несколько", "answer": "1,3"}
SHORT = {"id": 3, "level": 3, "type": "короткий", "answer": "strip|strip()|.strip()"}


class CheckAnswerTests(unittest.TestCase):
    def check(self, question, raw):
        return answers.check_answer(question, raw)

    def test_empty_is_no_answer_for_every_type(self):
        for question in (ONE, MANY, SHORT):
            self.assertEqual(self.check(question, ""), "нет ответа")
            self.assertEqual(self.check(question, "   "), "нет ответа")

    def test_single_choice(self):
        self.assertEqual(self.check(ONE, "2"), "верно")
        self.assertEqual(self.check(ONE, " 2 "), "верно")
        self.assertEqual(self.check(ONE, "3"), "неверно")
        self.assertEqual(self.check(ONE, "02"), "неверно")  # must be written as in the list

    def test_multiple_choice(self):
        self.assertEqual(self.check(MANY, "1,3"), "верно")
        self.assertEqual(self.check(MANY, "3, 1"), "верно")  # order and spaces do not matter
        self.assertEqual(self.check(MANY, "1"), "неверно")
        self.assertEqual(self.check(MANY, "1,3,4"), "неверно")
        self.assertEqual(self.check(MANY, "1,1,3"), "неверно")  # repeated number
        self.assertEqual(self.check(MANY, "1,01"), "неверно")

    def test_short_answer(self):
        self.assertEqual(self.check(SHORT, "strip()"), "верно")
        self.assertEqual(self.check(SHORT, "  STRIP "), "верно")
        self.assertEqual(self.check(SHORT, ".strip()"), "верно")
        self.assertEqual(self.check(SHORT, "split"), "неверно")

    def test_unknown_type_is_wrong_not_a_crash(self):
        self.assertEqual(self.check({"type": "эссе", "answer": "x"}, "x"), "неверно")


class LadderTests(unittest.TestCase):
    def test_next_level_moves_and_stays_inside_1_to_5(self):
        self.assertEqual(ladder.next_level(2, "верно"), 3)
        self.assertEqual(ladder.next_level(2, "неверно"), 1)
        self.assertEqual(ladder.next_level(5, "верно"), 5)
        self.assertEqual(ladder.next_level(1, "неверно"), 1)
        self.assertEqual(ladder.next_level(3, "нет ответа"), 3)

    def test_pick_question_prefers_wanted_level_and_list_order(self):
        questions = [{"id": 1, "level": 2}, {"id": 2, "level": 1}, {"id": 3, "level": 1}]
        self.assertEqual(ladder.pick_question(questions, 1, [])["id"], 2)
        self.assertEqual(ladder.pick_question(questions, 1, [2])["id"], 3)

    def test_pick_question_uses_nearest_level_lower_wins_a_tie(self):
        questions = [{"id": 1, "level": 4}, {"id": 2, "level": 2}]
        self.assertEqual(ladder.pick_question(questions, 3, [])["id"], 2)  # 2 and 4 are equally far
        self.assertEqual(ladder.pick_question(questions, 5, [])["id"], 1)

    def test_pick_question_returns_none_when_everything_was_asked(self):
        self.assertIsNone(ladder.pick_question([{"id": 1, "level": 1}], 1, [1]))
        self.assertIsNone(ladder.pick_question([], 1, []))


if __name__ == "__main__":
    unittest.main()
