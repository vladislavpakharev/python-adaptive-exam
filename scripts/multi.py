"""Multiple-choice question: option numbers separated by commas.

The right set is {1, 3}. Order and spaces do not matter. The answer is
"верно" only if every right option is named and nothing extra. A number out
of 1-4, a repeated number, an empty slot between commas or a non-number
makes the whole answer "нет ответа".
"""
import sys

print("""Какие из этих команд — функции Python?
1) print
2) cd
3) input
4) ls""")

CORRECT = {"1", "3"}
VALID = {"1", "2", "3", "4"}


def judge(line):
    line = line.strip()
    if line == "":
        return "нет ответа"
    parts = [part.strip() for part in line.split(",")]
    # every part must be a valid option number, and no number may repeat
    if any(part not in VALID for part in parts) or len(set(parts)) != len(parts):
        return "нет ответа"
    return "верно" if set(parts) == CORRECT else "неверно"


print(judge(sys.stdin.readline()))
