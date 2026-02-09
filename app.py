from flask import Flask, render_template, request, jsonify
import calendar
import json
import os
from datetime import date
from analysis import analyze_year

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

DATA_FILE = "data/notes.json"

# ======================
# INFRA BÁSICA
# ======================

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


def load_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ======================
# CALENDÁRIO (HOME)
# ======================

@app.route("/")
def calendar_view():
    year = int(request.args.get("year", date.today().year))
    data = load_data()

    months = []
    for m in range(1, 13):
        months.append({
            "name": calendar.month_name[m],
            "number": m,
            "weeks": calendar.monthcalendar(year, m)
        })

    return render_template(
        "calendar.html",
        months=months,
        year=year,
        notes=data
    )


# ======================
# DIA (ANOTAÇÃO)
# ======================

@app.route("/day/<int:year>/<int:month>/<int:day>", methods=["GET", "POST"])
def day_view(year, month, day):
    data = load_data()

    key = f"{year}-{month:02d}-{day:02d}"

    if request.method == "POST":
        text = request.form.get("text", "").strip()

        if key not in data:
            data[key] = {
                "text": text,
                "important": False
            }
        else:
            data[key]["text"] = text

        save_data(data)

    note = data.get(key, {"text": "", "important": False})

    return render_template(
        "day.html",
        year=year,
        month=month,
        day=day,
        note=note
    )


# ======================
# TOGGLE IMPORTANTE
# ======================

@app.route("/toggle-important", methods=["POST"])
def toggle_important():
    data = load_data()
    payload = request.json

    key = payload["key"]
    important = payload["important"]

    if key not in data:
        data[key] = {
            "text": "",
            "important": important
        }
    else:
        data[key]["important"] = important

    save_data(data)

    return jsonify({"status": "ok"})


# ======================
# DASHBOARD
# ======================

@app.route("/dashboard/<int:year>")
def dashboard(year):
    insights = analyze_year(year)
    return render_template(
        "dashboard.html",
        year=year,
        insights=insights
    )


# ======================
# 🤖 IA LOCAL (Perguntar IA)
# ======================

def generate_ai_response(question, data):
    burnout = data.get("burnout", 0)
    antifragile = data.get("antifragile", 0)
    predicted = data.get("predicted", 0)
    weekly = data.get("weekly", [])

    response_parts = []

    # Burnout
    if burnout > 70:
        response_parts.append(
            "Seu nível atual de burnout está alto. Considere reduzir carga e aumentar recuperação."
        )
    elif burnout > 40:
        response_parts.append(
            "Seu nível de estresse está moderado. Atenção ao acúmulo nas próximas semanas."
        )
    else:
        response_parts.append(
            "Seu nível atual de burnout está sob controle."
        )

    # Tendência
    if predicted > burnout + 10:
        response_parts.append(
            "A tendência indica aumento de pressão nos próximos 30 dias."
        )
    elif predicted < burnout - 10:
        response_parts.append(
            "A tendência indica recuperação progressiva."
        )
    else:
        response_parts.append(
            "A tendência futura está relativamente estável."
        )

    # Antifrágil
    if antifragile > 70:
        response_parts.append(
            "Seu sistema mental está adaptativo e resiliente."
        )
    elif antifragile < 40:
        response_parts.append(
            "Baixa antifragilidade detectada. Falta de recuperação ou excesso de pressão."
        )
    else:
        response_parts.append(
            "Nível moderado de adaptação ao estresse."
        )

    # Padrão semanal
    if weekly:
        max_day = weekly.index(max(weekly))
        days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
        response_parts.append(
            f"Seu dia de maior carga mental é: {days[max_day]}."
        )

    # Personalização pela pergunta
    q = question.lower()

    if "risco" in q or "colapso" in q:
        if burnout > 70 and predicted > 70:
            response_parts.append("Risco de colapso elevado.")
        else:
            response_parts.append("Risco de colapso controlado.")

    if "melhorar" in q or "como" in q:
        response_parts.append(
            "Sugestão: reduza picos de carga e distribua o esforço ao longo da semana."
        )

    return " ".join(response_parts)


@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    payload = request.json
    question = payload.get("question", "")
    data = payload.get("data", {})

    answer = generate_ai_response(question, data)

    return jsonify({"answer": answer})


# ======================
# RUN
# ======================

if __name__ == "__main__":
    app.run(debug=True)
