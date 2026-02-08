import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

DATA_FILE = "data/notes.json"

def load_notes():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def group_by_month(notes):
    grouped = defaultdict(list)
    for date_str, note in notes.items():
        ym = date_str[:7]  # YYYY-MM
        grouped[ym].append((date_str, note))
    return dict(grouped)

def sorted_days(notes):
    return sorted(
        [(datetime.strptime(d, "%Y-%m-%d"), n) for d, n in notes.items()],
        key=lambda x: x[0]
    )

def month_metrics(month_notes):
    total = len(month_notes)
    important = sum(1 for _, n in month_notes if n.get("important"))
    text_volume = sum(len(n.get("text", "")) for _, n in month_notes)
    intensity = important / total if total else 0
    return {
        "total": total,
        "important": important,
        "intensity": intensity,
        "text_volume": text_volume
    }

def historical_baseline(grouped):
    metrics = [month_metrics(m) for m in grouped.values() if m]
    if not metrics:
        return None
    return {
        "avg_important": sum(m["important"] for m in metrics) / len(metrics),
        "avg_intensity": sum(m["intensity"] for m in metrics) / len(metrics),
        "avg_text": sum(m["text_volume"] for m in metrics) / len(metrics)
    }

def burnout_risk(notes, baseline):
    if not baseline:
        return None
    days = sorted_days(notes)
    if len(days) < 7:
        return None
    last_14 = days[-14:]
    imp = sum(1 for _, n in last_14 if n.get("important"))
    text = sum(len(n.get("text", "")) for _, n in last_14)
    score = 0
    if imp >= baseline["avg_important"] * 0.6:
        score += 1
    if text >= baseline["avg_text"] * 0.7:
        score += 1
    if imp >= 5:
        score += 1
    if score == 1:
        return "🟡 Risco leve de sobrecarga contínua."
    elif score == 2:
        return "🟠 Risco moderado de burnout."
    elif score >= 3:
        return "🔴 Risco elevado de burnout. Considere pausa estratégica."
    return None

def weekly_projection(notes):
    days = sorted_days(notes)
    if len(days) < 7:
        return None
    last_7 = days[-7:]
    important = sum(1 for _, n in last_7 if n.get("important"))
    if important >= 4:
        return "📆 Próxima semana tende a ser INTENSA se o ritmo continuar."
    elif important >= 2:
        return "📆 Próxima semana tende a ser MODERADA."
    else:
        return "📆 Próxima semana tende a ser LEVE."

def simulation_hint(month_notes):
    important = sum(1 for _, n in month_notes if n.get("important"))
    if important >= 6:
        return "🧪 Simulação: adicionar mais dias importantes aumenta risco de fadiga."
    elif important <= 2:
        return "🧪 Simulação: há margem segura para novos compromissos."
    return None

def strategic_report():
    notes = load_notes()
    grouped = group_by_month(notes)
    baseline = historical_baseline(grouped)
    report = {}
    for month, month_notes in grouped.items():
        insights = []
        metrics = month_metrics(month_notes)
        insights.append(
            f"📊 Importantes: {metrics['important']} | Intensidade: {metrics['intensity']:.2f}"
        )
        sim = simulation_hint(month_notes)
        if sim:
            insights.append(sim)
        report[month] = insights
    burnout = burnout_risk(notes, baseline)
    if burnout:
        report.setdefault("global", []).append(burnout)
    weekly = weekly_projection(notes)
    if weekly:
        report.setdefault("global", []).append(weekly)
    return report

if __name__ == "__main__":
    report = strategic_report()
    for period, insights in report.items():
        print(f"\n📅 {period}")
        for i in insights:
            print("-", i)
