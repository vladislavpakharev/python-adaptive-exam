"""Short-answer question. Reads one line from stdin and prints a verdict.

    $ python3 scripts/answer.py
    Какая функция Python печатает текст на экран?
    print
    верно

Rules: spaces and letter case do not matter, "print()" is accepted too,
an empty line or the end of input means "нет ответа". Exit code is always 0.
"""
import sys

print("Какая функция Python печатает текст на экран?")
line = sys.stdin.readline().strip().lower()

if line == "":
    print("нет ответа")
elif line in ("print", "print()"):
    print("верно")
else:
    print("неверно")
