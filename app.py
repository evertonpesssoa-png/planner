from flask import Flask, render_template, request, jsonify
import calendar, json, os
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
# DIA (ANOTAÇÃO + BOTÃO SALVAR)
# ======================
@app.route("/day/<int:year>/<int:month>/<int:day>", methods=["GET", "POST"])
def day_view(year, month, day):
    data = load_data()

    # 🔑 chave padronizada (ESSENCIAL)
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
# ✅ TOGGLE DO CHECKBOX (AUTO-SAVE)
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


if __name__ == "__main__":
    app.run(debug=True)
