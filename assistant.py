from datetime import datetime, timedelta
import re

def load_notes(raw_data: dict):
    notes = []
    for date, content in raw_data.items():
        notes.append({
            "date": date,
            "text": content.get("text", ""),
            "important": content.get("important", False)
        })
    return notes

def simple_search(keyword: str, notes: list):
    keyword = keyword.lower()
    return [n for n in notes if keyword in n["text"].lower()]

def list_important_days(notes: list):
    return [n for n in notes if n["important"]]

def summary(notes: list):
    if not notes:
        return "📭 Nenhuma anotação encontrada."
    important = len([n for n in notes if n["important"]])
    avg_size = sum(len(n["text"]) for n in notes) // len(notes)
    return (
        f"📊 Resumo geral:\n"
        f"- Total de anotações: {len(notes)}\n"
        f"- Dias importantes: {important}\n"
        f"- Tamanho médio das anotações: {avg_size} caracteres"
    )

def detect_patterns(notes: list):
    important = list_important_days(notes)
    if len(important) >= 5:
        return "⚠️ Muitos dias importantes registrados. Atenção à sobrecarga."
    if not important:
        return "🌱 Nenhum dia importante registrado. Período tranquilo."
    return "📈 Ritmo equilibrado de compromissos."

def detect_intent(question: str):
    q = question.lower()
    if any(w in q for w in ["importante", "compromisso", "agenda"]):
        return "important"
    if any(w in q for w in ["resumo", "estatística", "dados"]):
        return "summary"
    if any(w in q for w in ["padrão", "ciclo", "ritmo"]):
        return "pattern"
    if any(w in q for w in ["aconteceu", "fiz", "teve"]):
        return "search"
    return "unknown"

def update_memory(memory: dict, question: str, response: str):
    memory["last_question"] = question
    memory["last_response"] = response
    memory["timestamp"] = datetime.now().isoformat()

def parse_time_window(question: str):
    q = question.lower()
    today = datetime.today()
    if "últimos 7 dias" in q or "ultimos 7 dias" in q:
        return today - timedelta(days=7), today
    if "essa semana" in q:
        start = today - timedelta(days=today.weekday())
        return start, today
    if "esse mês" in q or "este mês" in q:
        start = today.replace(day=1)
        return start, today
    if "mês passado" in q or "mes passado" in q:
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        start = last_month_end.replace(day=1)
        return start, last_month_end
    if "esse ano" in q:
        start = today.replace(month=1, day=1)
        return start, today
    return None, None

def answer_question(question: str, raw_data: dict, memory: dict):
    notes = load_notes(raw_data)
    intent = detect_intent(question)
    start, end = parse_time_window(question)
    filtered_notes = notes
    if start and end:
        filtered_notes = [
            n for n in notes
            if start.date() <= datetime.strptime(n["date"], "%Y-%m-%d").date() <= end.date()
        ]
    if intent == "important":
        important = list_important_days(filtered_notes)
        if not important:
            response = "🌱 Nenhum compromisso importante nesse período."
        else:
            response = "⭐ Compromissos importantes:\n\n"
            for n in important:
                response += f"⭐ {n['date'][8:10]}/{n['date'][5:7]}: {n['text'][:60]}\n"
            if len(important) >= 5:
                response += "\n⚠️ Muitos compromissos concentrados."
    elif intent == "summary":
        response = summary(filtered_notes)
    elif intent == "pattern":
        response = detect_patterns(filtered_notes)
    elif intent == "search":
        words = re.findall(r"\w+", question.lower())
        matches = []
        for w in words:
            matches.extend(simple_search(w, filtered_notes))
        if not matches:
            response = "📭 Não encontrei registros relacionados."
        else:
            response = "🔎 Encontrei registros:\n\n"
            for n in matches[:5]:
                response += f"- {n['date']}: {n['text'][:60]}\n"
    else:
        response = "🤔 Não entendi totalmente. Tente perguntar sobre compromissos, resumos ou períodos."
    update_memory(memory, question, response)
    return response
