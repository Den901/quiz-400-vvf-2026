from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"br", "p", "div", "li"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "div", "li"}:
            self.parts.append(" ")


def clean_markup(value: object) -> str:
    parser = TextExtractor()
    parser.feed(html.unescape(str(value or "")))
    return re.sub(r"\s+", " ", "".join(parser.parts)).strip()


def fingerprint(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).casefold()
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa un'esportazione autorizzata di quiz di storia.")
    parser.add_argument("source", type=Path)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8-sig"))
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    existing = {fingerprint(str(row.get("text") or "")) for row in dataset if isinstance(row, dict)}
    incoming_seen: set[str] = set()
    imported: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []

    sections = source.get("data", {}).get("sezione", [])
    rows = [quiz for section in sections if isinstance(section, dict) for quiz in section.get("quiz", []) if isinstance(quiz, dict)]
    for row in rows:
        quiz_id = row.get("quizId")
        question = clean_markup(row.get("title"))
        choices = row.get("choices") if isinstance(row.get("choices"), list) else []
        answers = [clean_markup(choice.get("text")) for choice in choices if isinstance(choice, dict)]
        correct_values = {str(value) for value in row.get("correctAnswer", [])}
        correct_indexes = [index for index, choice in enumerate(choices) if isinstance(choice, dict) and str(choice.get("value")) in correct_values]
        key = fingerprint(question)
        reason = None
        if not quiz_id or not question or len(answers) < 2 or len(answers) != len(choices) or len(correct_indexes) != 1:
            reason = "struttura non valida"
        elif key in existing:
            reason = "duplicato della banca dati"
        elif key in incoming_seen:
            reason = "duplicato nel file"
        if reason:
            skipped.append({"quizId": quiz_id, "reason": reason, "question": question})
            continue
        correct = correct_indexes[0]
        imported.append({
            "id": f"simone-history-{quiz_id}",
            "category": "storia",
            "text": question,
            "answers": answers,
            "correct": correct,
            "explanation": f"La risposta corretta indicata nella banca dati è: {answers[correct]}",
            "image": "",
        })
        incoming_seen.add(key)
        existing.add(key)

    args.dataset.write_text(json.dumps(dataset + imported, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {"sourceQuestions": len(rows), "imported": len(imported), "skipped": len(skipped), "skippedItems": skipped}
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "skippedItems"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
