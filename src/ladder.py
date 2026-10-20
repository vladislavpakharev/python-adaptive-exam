"""Choosing the next question: the difficulty "ladder".

Correct answer -> one level up, wrong answer -> one level down (never below 1
or above 5), no answer -> the level stays the same.
"""

START_LEVEL = 1
MIN_LEVEL = 1
MAX_LEVEL = 5


def next_level(level, result):
    """Level of the next question after an answer at `level`."""
    if result == "верно":
        return min(level + 1, MAX_LEVEL)
    if result == "неверно":
        return max(level - 1, MIN_LEVEL)
    return level


def pick_question(questions, level, asked):
    """First not yet asked question of the wanted level.

    If that level has no questions left, the nearest level is used; when two
    levels are equally close the lower one wins. Returns None when every
    question has been asked.
    """
    for distance in range(MAX_LEVEL):
        for wanted in (level - distance, level + distance):  # lower level first
            for question in questions:
                if question["level"] == wanted and question["id"] not in asked:
                    return question
    return None
