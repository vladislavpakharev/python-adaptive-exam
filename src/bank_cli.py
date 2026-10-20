"""Command line tool for inspecting a question bank.

    python3 src/bank_cli.py BANK.csv              number of questions
    python3 src/bank_cli.py BANK.csv --show ID    print one question
    python3 src/bank_cli.py BANK.csv --stats      questions per level and topic
    python3 src/bank_cli.py BANK.csv --matrix     topic x level table
"""

import sys

import bank


def show(questions, raw_id):
    question = None
    if raw_id.isdigit():
        question = bank.find_question(questions, int(raw_id))
    if question is None:
        print("Нет вопроса с id " + raw_id)
        return 1
    for line in bank.question_lines(question):
        print(line)
    return 0


def stats(questions):
    levels = bank.count_levels(questions)
    for level in bank.LEVELS:
        print("Уровень %d: %d" % (level, levels[level]))
    topics = bank.count_topics(questions)
    for topic in bank.TOPICS:
        print("%s: %d" % (topic, topics[topic]))
    return 0


def matrix(questions):
    table = bank.count_matrix(questions)
    print("\t".join(["тема"] + [str(level) for level in bank.LEVELS]))
    for topic in bank.TOPICS:
        print("\t".join([topic] + [str(table[topic][level]) for level in bank.LEVELS]))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("Запуск: python3 src/bank_cli.py ПУТЬ_К_БАНКУ [--show ID | --stats | --matrix]")
        return 1
    path, flags = argv[0], argv[1:]
    try:
        questions, skipped = bank.load_bank(path)
    except FileNotFoundError:
        print("Файл не найден: " + path)
        return 1

    if not flags:
        print("Вопросов: %d" % len(questions))
        if skipped:
            print("Пропущено строк: %d" % skipped)
        return 0
    if flags[0] == "--show":
        return show(questions, flags[1] if len(flags) > 1 else "")
    if flags[0] == "--stats":
        return stats(questions)
    if flags[0] == "--matrix":
        return matrix(questions)
    print("Неизвестный флаг: " + flags[0])
    return 1


if __name__ == "__main__":
    sys.exit(main())
