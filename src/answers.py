"""Checking a person's answer against a question from the bank."""

CORRECT = "верно"
WRONG = "неверно"
NO_ANSWER = "нет ответа"


def _check_single(raw, correct):
    # The number must be written exactly as in the list: "02" is wrong.
    return raw == correct


def _check_multiple(raw, correct):
    given = [item.strip() for item in raw.split(",")]
    expected = [item.strip() for item in correct.split(",")]
    if len(given) != len(set(given)):  # every option may be named only once
        return False
    return sorted(given) == sorted(expected)  # order does not matter


def _check_short(raw, correct):
    forms = [form.strip().lower() for form in correct.split("|")]
    return raw.lower() in forms


CHECKERS = {
    "один": _check_single,
    "несколько": _check_multiple,
    "короткий": _check_short,
}


def check_answer(question, raw):
    """Return "верно", "неверно" or "нет ответа".

    An empty answer (or only spaces) is "нет ответа" for every question type.
    Anything else is an answer, either right or wrong.
    """
    raw = raw.strip()
    if raw == "":
        return NO_ANSWER

    checker = CHECKERS.get(question["type"])
    if checker is None:
        return WRONG
    return CORRECT if checker(raw, question["answer"]) else WRONG
