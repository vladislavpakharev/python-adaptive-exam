import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bank  # noqa: E402
import exam  # noqa: E402


def questions_from_file():
    questions, _ = bank.load_bank(exam.DEFAULT_BANK)
    return questions


def drive(inputs, **options):
    """Run an exam with scripted input; return (summary, printed lines)."""
    feed = iter(inputs)
    printed = []
    summary = exam.run_exam(questions_from_file(), lambda: next(feed, None), printed.append, **options)
    return summary, printed


class RuleTests(unittest.TestCase):
    def test_final_level_is_the_last_correct_one(self):
        history = [(1, "верно"), (2, "неверно"), (1, "верно"), (2, "неверно")]
        self.assertEqual(exam.final_level(history), 1)
        self.assertIsNone(exam.final_level([(1, "неверно"), (1, "нет ответа")]))
        self.assertIsNone(exam.final_level([]))

    def test_stable_level_needs_two_correct_answers(self):
        history = [(1, "верно"), (2, "верно"), (2, "верно"), (3, "верно")]
        self.assertEqual(exam.stable_level(history), 2)
        self.assertIsNone(exam.stable_level([(1, "верно"), (2, "верно")]))

    def test_result_line_and_screen(self):
        self.assertEqual(exam.result_line("нет ответа"), "Нет ответа.")
        question = questions_from_file()[0]
        screen = exam.question_screen(1, question)
        self.assertEqual(screen[0], "Вопрос 1 из 10")
        self.assertEqual(screen[-1], "Введи номер варианта.")


class RunExamTests(unittest.TestCase):
    def test_input_ending_at_once_does_not_start_the_exam(self):
        summary, printed = drive([])
        self.assertIsNone(summary)
        self.assertEqual(printed, ["Как тебя зовут?", "Экзамен не начат."])

    def test_name_is_cleaned_for_the_csv_format(self):
        summary, _ = drive(["a;b", None], max_questions=1)
        self.assertEqual(summary["name"], "a b")
        summary, _ = drive(["  ", None], max_questions=1)
        self.assertEqual(summary["name"], "без имени")

    def test_correct_answer_is_counted(self):
        # Level 1 first question is id 1 (answer 2), then the ladder goes up.
        questions = {q["id"]: q for q in questions_from_file()}
        summary, printed = drive(["Анна", "2"], max_questions=1)
        self.assertEqual(summary, {"name": "Анна", "level": 1, "asked": 1, "correct": 1})
        self.assertIn("Итог: уровень 1.", printed)
        self.assertEqual(questions[1]["answer"], "2")

    def test_all_wrong_gives_undefined_level(self):
        summary, printed = drive(["Боб", "9", "9", "9"], max_questions=3)
        self.assertIsNone(summary["level"])
        self.assertEqual(summary["correct"], 0)
        self.assertIn("Итог: не определён.", printed)

    def test_end_of_input_stops_after_recording_no_answer(self):
        summary, printed = drive(["Вика"])  # no answers at all
        self.assertEqual(summary["asked"], 1)
        self.assertIn("Нет ответа.", printed)

    def test_respects_the_question_limit(self):
        summary, printed = drive(["Тест"] + ["1"] * 40, max_questions=10)
        self.assertEqual(summary["asked"], 10)
        shown = [line for line in printed if line.startswith("Вопрос ")]
        self.assertEqual(len(shown), 10)

    def test_stable_rule_changes_the_verdict_text(self):
        _, printed = drive(["Лена", "9", "9"], max_questions=2, stable=True)
        self.assertIn("Итог: не определён.", printed)
        self.assertTrue(any("хотя бы два" in line for line in printed))


class ResultFileTests(unittest.TestCase):
    def test_save_result_appends_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "results.csv"
            exam.save_result(path, "Анна", 3, 10, 6)
            exam.save_result(path, "Боб", None, 4, 0)
            self.assertEqual(path.read_text(encoding="utf-8"),
                             "Анна;3;10;6\nБоб;не определён;4;0\n")


if __name__ == "__main__":
    unittest.main()
