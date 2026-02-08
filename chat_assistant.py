from assistant import answer_question
import json
import os

DATA_FILE = "data/notes.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

memory = {}

print("🧠 Assistente do Planner iniciado")
print("Digite sua pergunta ou 'sair'\n")

while True:
    question = input("🧠 Pergunte algo (ou 'sair'): ").strip()
    if question.lower() in ["sair", "exit", "quit"]:
        print("👋 Encerrando assistente")
        break
    data = load_data()
    response = answer_question(question, data, memory)
    print("\n" + response + "\n")
