#!/bin/bash
# Quick look at a question bank. Prints exactly six lines:
#   number of questions, the first three questions as written in the file,
#   number of questions on the topic "строки", number of level-1 questions.
# Usage (from the repository root): bash scripts/explore.sh [BANK.csv]

BANK="${1:-data/python_basics.csv}"

tail -n +2 "$BANK" | wc -l | tr -d ' '                    # header is not a question
sed -n '2,4p' "$BANK"                                      # first three questions
awk -F';' 'NR > 1 && $2 == "строки"' "$BANK" | wc -l | tr -d ' '
awk -F';' 'NR > 1 && $3 == "1"' "$BANK" | wc -l | tr -d ' '
