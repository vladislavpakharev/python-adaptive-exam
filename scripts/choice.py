"""Single-choice question: the person types the number of one option (1-4).

The right option is 2. Spaces around the number do not matter. Anything that
is not a single digit from 1 to 4 (5, "два", an empty line) is "нет ответа".
"""
import sys

print("""Что напечатает print(2 + 3)?
1) 23
2) 5
3) 2 + 3
4) ошибка""")

line = sys.stdin.readline().strip()

if line not in ("1", "2", "3", "4"):
    print("нет ответа")
elif line == "2":
    print("верно")
else:
    print("неверно")
