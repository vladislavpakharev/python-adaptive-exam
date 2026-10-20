"""The first-stage scripts are checked the way the exam checks any program:
feed an answer through stdin and compare the printed verdict."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verdict(script, answer):
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], input=answer,
                          capture_output=True, text=True, encoding="utf-8")
    assert done.returncode == 0, done.stderr  # "no answer" is text, never an error
    return done.stdout.strip().splitlines()[-1]


class AnswerScriptTests(unittest.TestCase):
    def test_table(self):
        cases = [("print\n", "верно"), (" PRINT\n", "верно"), ("print()\n", "верно"),
                 ("input\n", "неверно"), ("pri nt\n", "неверно"), ("\n", "нет ответа"),
                 ("", "нет ответа")]
        for given, want in cases:
            self.assertEqual(verdict("answer.py", given), want, repr(given))


class ChoiceScriptTests(unittest.TestCase):
    def test_table(self):
        cases = [("2\n", "верно"), (" 2 \n", "верно"), ("4\n", "неверно"), ("1\n", "неверно"),
                 ("3\n", "неверно"), ("5\n", "нет ответа"), ("два\n", "нет ответа"),
                 ("\n", "нет ответа"), ("", "нет ответа")]
        for given, want in cases:
            self.assertEqual(verdict("choice.py", given), want, repr(given))


class MultiScriptTests(unittest.TestCase):
    def test_table(self):
        cases = [("1,3\n", "верно"), ("3, 1\n", "верно"), ("1\n", "неверно"),
                 ("1,3,4\n", "неверно"), ("1,5\n", "нет ответа"), ("1,1,3\n", "нет ответа"),
                 ("1,,3\n", "нет ответа"), ("a,3\n", "нет ответа"), ("\n", "нет ответа"),
                 ("", "нет ответа")]
        for given, want in cases:
            self.assertEqual(verdict("multi.py", given), want, repr(given))


class ExploreScriptTests(unittest.TestCase):
    def test_prints_six_lines_computed_from_the_file(self):
        done = subprocess.run(["bash", "scripts/explore.sh"], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8")
        lines = done.stdout.splitlines()
        self.assertEqual(len(lines), 6)
        self.assertEqual(lines[0], "35")
        self.assertEqual(lines[4], "9")   # questions on the topic "строки"
        self.assertEqual(lines[5], "7")   # level-1 questions


if __name__ == "__main__":
    unittest.main()
