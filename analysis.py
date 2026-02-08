# analysis.py
import json
import os
import calendar
from datetime import datetime
from collections import defaultdict

DATA_FILE = "data/notes.json"


# =========================
# Carregamento de dados
# =========================
def load_notes():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# Análise base
# =========================
def analyze_notes(notes: dict):
    total_notes = 0
    important_days = 0
    total_chars = 0

    for note in notes.values():
        text = note.get("text", "").strip()
        important = note.get("important", False)

        if text:
            total_notes += 1
            total_chars += len(text)

        if important:
            important_days += 1

    avg_chars = round(total_chars / total_notes, 1) if total_notes > 0 else 0

    insight = generate_insight(
        total_notes,
        important_days,
        avg_chars
    )

    return {
        "total_notes": total_notes,
        "important_days": important_days,
        "avg_chars": avg_chars,
        "insight": insight
    }


def generate_insight(total, important, avg_chars):
    if total == 0:
        return (
            "Ainda não há anotações suficientes para análise. "
            "Comece registrando seus dias para gerar insights."
        )

    messages = []

    if total <= 3:
        messages.append(
            "Você fez poucas anotações até agora, indicando um uso pontual do diário."
        )
    else:
        messages.append(
            f"Você já registrou {total} dias, criando um histórico consistente."
        )

    if important > 0:
        messages.append(
            f"{important} dia(s) foram marcados como importantes."
        )
    else:
        messages.append(
            "Nenhum dia foi marcado como importante até o momento."
        )

    if avg_chars < 80:
        messages.append("As anotações são curtas e objetivas.")
    elif avg_chars < 250:
        messages.append("As anotações indicam reflexões moderadas.")
    else:
        messages.append("As anotações são longas e profundas.")

    return " ".join(messages)


# =========================
# 🔥 Análise anual (dashboard)
# =========================
def analyze_year(year: int):
    all_notes = load_notes()

    year_notes = {
        date: note
        for date, note in all_notes.items()
        if date.startswith(str(year))
    }

    base = analyze_notes(year_notes)

    monthly_activity = defaultdict(int)
    weekday_distribution = defaultdict(int)

    for date_str, note in year_notes.items():
        y, m, d = map(int, date_str.split("-"))
        monthly_activity[m] += 1

        if note.get("important"):
            weekday = calendar.day_name[
                datetime(y, m, d).weekday()
            ]
            weekday_distribution[weekday] += 1

    busiest_month = (
        max(monthly_activity, key=monthly_activity.get)
        if monthly_activity else None
    )

    return {
        "year": year,
        "total_days_with_notes": base["total_notes"],
        "important_days": base["important_days"],
        "avg_text_size": base["avg_chars"],
        "insight": base["insight"],
        "monthly_activity": dict(monthly_activity),
        "busiest_month": busiest_month,
        "weekday_distribution": dict(weekday_distribution)
    }
