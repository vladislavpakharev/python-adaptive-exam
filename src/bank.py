"""Question bank: reading the CSV file and simple statistics.

The module never prints anything. It returns data, the callers (bank_cli.py,
exam.py) decide what to show.

File format (UTF-8, ';' separated, first line is a header):

    id;тема;уровень;тип;вопрос;варианты;ответ

* the text may contain the two characters ``\\n`` that stand for a line break;
* options are separated with '|' (empty for short-answer questions).
"""

TOPICS = ["строки", "числа", "списки", "ошибки"]
LEVELS = [1, 2, 3, 4, 5]
FIELD_COUNT = 7


def _is_broken(line):
    """True if a data line cannot be turned into a question."""
    if line.strip() == "":
        return True
    fields = line.split(";")
    if len(fields) != FIELD_COUNT:
        return True
    if not fields[0].isdigit():
        return True
    return fields[2] not in [str(level) for level in LEVELS]


def _to_question(line):
    qid, topic, level, kind, text, options, answer = line.split(";")
    return {
        "id": int(qid),
        "topic": topic,
        "level": int(level),
        "type": kind,
        "text": text.replace("\\n", "\n"),
        "options": options.split("|") if options != "" else [],
        "answer": answer,
    }


def load_bank(path):
    """Read a bank file.

    Returns ``(questions, skipped)``: the list of question dictionaries and the
    number of broken lines that were left out. A missing file raises
    ``FileNotFoundError`` - the caller decides how to report it.
    """
    with open(path, encoding="utf-8") as source:
        lines = source.read().splitlines()

    questions = []
    skipped = 0
    for line in lines[1:]:  # lines[0] is the header
        if _is_broken(line):
            skipped += 1
            continue
        questions.append(_to_question(line))
    return questions, skipped


def find_question(questions, qid):
    """Return the question with the given numeric id, or None."""
    for question in questions:
        if question["id"] == qid:
            return question
    return None


def question_lines(question):
    """Lines a person sees on screen: the text first, then '1) ...' options."""
    lines = question["text"].split("\n")
    for number, option in enumerate(question["options"], start=1):
        lines.append("%d) %s" % (number, option))
    return lines


def count_levels(questions):
    """{level: number of questions}; every level 1-5 is present."""
    counts = {level: 0 for level in LEVELS}
    for question in questions:
        counts[question["level"]] += 1
    return counts


def count_topics(questions):
    """{topic: number of questions}; every known topic is present."""
    counts = {topic: 0 for topic in TOPICS}
    for question in questions:
        counts[question["topic"]] = counts.get(question["topic"], 0) + 1
    return counts


def count_matrix(questions):
    """{topic: {level: number}} - how many questions per topic and level."""
    table = {topic: {level: 0 for level in LEVELS} for topic in TOPICS}
    for question in questions:
        row = table.setdefault(question["topic"], {level: 0 for level in LEVELS})
        row[question["level"]] += 1
    return table
