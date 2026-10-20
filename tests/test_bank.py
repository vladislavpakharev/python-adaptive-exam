import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bank  # noqa: E402

HEADER = "id;тема;уровень;тип;вопрос;варианты;ответ"
GOOD_SHORT = r"1;списки;2;короткий;Что напечатает код?\nitems = [3, 1, 2]\nprint(items[0]);;3"
GOOD_ONE = "2;строки;1;один;Что возвращает input()?;строку|число|список|ничего;1"


def write_bank(lines):
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    handle.write("\n".join(lines) + "\n")
    handle.close()
    return handle.name


class LoadBankTests(unittest.TestCase):
    def test_reads_all_fields_and_types(self):
        questions, skipped = bank.load_bank(write_bank([HEADER, GOOD_SHORT, GOOD_ONE]))
        self.assertEqual(skipped, 0)
        self.assertEqual(len(questions), 2)
        first = questions[0]
        self.assertEqual((first["id"], first["level"]), (1, 2))
        self.assertIsInstance(first["id"], int)
        self.assertEqual(first["options"], [])
        self.assertEqual(first["answer"], "3")
        self.assertEqual(questions[1]["options"], ["строку", "число", "список", "ничего"])

    def test_backslash_n_becomes_real_line_break(self):
        questions, _ = bank.load_bank(write_bank([HEADER, GOOD_SHORT]))
        self.assertEqual(questions[0]["text"].split("\n")[0], "Что напечатает код?")
        self.assertEqual(len(questions[0]["text"].split("\n")), 3)

    def test_broken_lines_are_skipped_and_counted(self):
        broken = [
            "",                                   # empty line
            "3;строки;1;один;мало полей",         # wrong field count
            "x;строки;1;один;Q;a|b;1",            # id is not a number
            "4;строки;9;один;Q;a|b;1",            # level out of range
        ]
        questions, skipped = bank.load_bank(write_bank([HEADER, GOOD_ONE] + broken))
        self.assertEqual([q["id"] for q in questions], [2])
        self.assertEqual(skipped, 4)

    def test_missing_file_is_not_swallowed(self):
        with self.assertRaises(FileNotFoundError):
            bank.load_bank("/no/such/bank.csv")


class HelpersTests(unittest.TestCase):
    def setUp(self):
        self.questions, _ = bank.load_bank(write_bank([HEADER, GOOD_SHORT, GOOD_ONE]))

    def test_find_question(self):
        self.assertEqual(bank.find_question(self.questions, 2)["topic"], "строки")
        self.assertIsNone(bank.find_question(self.questions, 99))

    def test_question_lines_numbers_the_options(self):
        lines = bank.question_lines(self.questions[1])
        self.assertEqual(lines[0], "Что возвращает input()?")
        self.assertEqual(lines[1:], ["1) строку", "2) число", "3) список", "4) ничего"])

    def test_question_lines_without_options(self):
        self.assertEqual(len(bank.question_lines(self.questions[0])), 3)

    def test_counts(self):
        self.assertEqual(bank.count_levels(self.questions), {1: 1, 2: 1, 3: 0, 4: 0, 5: 0})
        topics = bank.count_topics(self.questions)
        self.assertEqual((topics["строки"], topics["списки"], topics["числа"]), (1, 1, 0))
        matrix = bank.count_matrix(self.questions)
        self.assertEqual(matrix["списки"][2], 1)
        self.assertEqual(matrix["строки"][1], 1)
        self.assertEqual(matrix["ошибки"][5], 0)


class RealBankTests(unittest.TestCase):
    def test_shipped_bank_is_clean_and_covers_every_level(self):
        questions, skipped = bank.load_bank(ROOT / "data" / "python_basics.csv")
        self.assertEqual(skipped, 0)
        self.assertEqual(len(questions), 35)
        self.assertTrue(all(count > 0 for count in bank.count_levels(questions).values()))
        self.assertEqual(len({q["id"] for q in questions}), len(questions))


if __name__ == "__main__":
    unittest.main()
