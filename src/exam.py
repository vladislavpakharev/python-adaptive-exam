"""Adaptive exam: a conversation with the person and the final level.

    python3 src/exam.py                          default bank, default rule
    python3 src/exam.py --stable                 "stable level" rule
    python3 src/exam.py --bank A.csv B.csv       questions from several files
    python3 src/exam.py --results out.csv --max 5

The functions at the top only build text or numbers. run_exam() does the
conversation through two small callbacks, so tests can drive it without a
terminal. Only main() touches files, stdin and stdout.
"""

import argparse
import sys
from pathlib import Path

import answers
import bank
import ladder

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK = ROOT / "data" / "python_basics.csv"
DEFAULT_RESULTS = "results.csv"
MAX_QUESTIONS = 10

HINTS = {
    "один": "Введи номер варианта.",
    "несколько": "Введи номера всех верных вариантов через запятую.",
    "короткий": "Напиши ответ.",
}


def load_questions(paths):
    """All questions of the given files in one list (file order is kept)."""
    questions = []
    for path in paths:
        loaded, _ = bank.load_bank(path)
        questions.extend(loaded)
    return questions


def question_screen(number, question, total=MAX_QUESTIONS):
    """Lines printed for one question."""
    lines = ["Вопрос %d из %d" % (number, total)]
    lines.extend(bank.question_lines(question))
    hint = HINTS.get(question["type"])
    if hint is not None:
        lines.append(hint)
    return lines


def result_line(result):
    """'верно' -> 'Верно.'"""
    return result.capitalize() + "."


def final_level(history):
    """Rule 1: the level of the last correct answer, or None.

    history is a list of (question level, result) pairs in exam order.
    """
    for level, result in reversed(history):
        if result == answers.CORRECT:
            return level
    return None


def final_lines(level):
    if level is None:
        return ["Итог: не определён.", "Почему: ни одного правильного ответа."]
    return ["Итог: уровень %d." % level,
            "Почему: последний правильный ответ — на уровне %d." % level]


def stable_level(history):
    """Rule 2: the highest level with at least two correct answers, or None."""
    counts = {}
    for level, result in history:
        if result == answers.CORRECT:
            counts[level] = counts.get(level, 0) + 1
    stable = [level for level, count in counts.items() if count >= 2]
    return max(stable) if stable else None


def stable_lines(level):
    if level is None:
        return ["Итог: не определён.",
                "Почему: нет уровня, на котором было хотя бы два правильных ответа."]
    return ["Итог: уровень %d." % level,
            "Почему: на этом уровне было хотя бы два правильных ответа."]


def save_result(path, name, level, asked, correct):
    """Append the line 'name;level;asked;correct' to the results file."""
    level_text = "не определён" if level is None else str(level)
    with open(path, "a", encoding="utf-8") as target:
        target.write("%s;%s;%d;%d\n" % (name, level_text, asked, correct))


def run_exam(questions, read_line, write, max_questions=MAX_QUESTIONS, stable=False):
    """Run one exam.

    read_line() returns the next line typed by the person, or None when the
    input has ended. write(text) prints one line. Returns a summary dictionary,
    or None when the exam was not started.
    """
    write("Как тебя зовут?")
    name = read_line()
    if name is None:
        write("Экзамен не начат.")
        return None
    name = name.replace(";", " ").strip() or "без имени"

    level = ladder.START_LEVEL
    asked = []
    history = []
    while len(asked) < max_questions:
        question = ladder.pick_question(questions, level, asked)
        if question is None:
            break
        asked.append(question["id"])
        write("")
        for line in question_screen(len(asked), question, max_questions):
            write(line)
        raw = read_line()
        result = answers.check_answer(question, raw if raw is not None else "")
        write(result_line(result))
        history.append((question["level"], result))
        level = ladder.next_level(question["level"], result)
        if raw is None:  # input ended: stop after recording the empty answer
            break

    if stable:
        result_level = stable_level(history)
        lines = stable_lines(result_level)
    else:
        result_level = final_level(history)
        lines = final_lines(result_level)
    write("")
    for line in lines:
        write(line)

    correct = sum(1 for _, result in history if result == answers.CORRECT)
    return {"name": name, "level": result_level, "asked": len(asked), "correct": correct}


def _stdin_line():
    line = sys.stdin.readline()
    return None if line == "" else line.rstrip("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Adaptive Python exam")
    parser.add_argument("--bank", nargs="+", default=[str(DEFAULT_BANK)],
                        help="one or more question bank files")
    parser.add_argument("--results", default=DEFAULT_RESULTS, help="file for result lines")
    parser.add_argument("--stable", action="store_true", help="use the stable level rule")
    parser.add_argument("--max", type=int, default=MAX_QUESTIONS, dest="max_questions")
    args = parser.parse_args(argv)

    try:
        questions = load_questions(args.bank)
    except FileNotFoundError as error:
        print("Файл не найден: %s" % error.filename)
        return 1

    summary = run_exam(questions, _stdin_line, print, args.max_questions, args.stable)
    if summary is not None:
        save_result(args.results, summary["name"], summary["level"],
                    summary["asked"], summary["correct"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
