from datetime import datetime

class Memory:
    def __init__(self):
        self.short_term = []  # últimos 20 comandos
        self.long_term = []   # histórico completo

    def update(self, question, answer):
        record = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
        self.short_term.append(record)
        self.long_term.append(record)

        # mantém apenas últimos 20 na memória de curto prazo
        if len(self.short_term) > 20:
            self.short_term.pop(0)
