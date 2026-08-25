from langchain_ollama import OllamaLLM


llm = OllamaLLM(model="qwen2.5:7b-instruct")


def classify_request(request_text: str) -> str:
    prompt = f"""
Ти класифікатор внутрішніх запитів AI-юніту.

Проаналізуй наступний запит:

---
{request_text}
---

Поверни результат ТІЛЬКИ у форматі JSON.

Обов'язкові поля:

- "category" — одне з:
  "автоматизація",
  "інтеграція",
  "звіт/аналітика",
  "баг/підтримка",
  "питання/консультація",
  "поза скоупом"

- "target_department" — відділ-замовник.
  Якщо визначити неможливо — null.

- "priority" — одне з:
  "low",
  "medium",
  "high".
  Визначай за терміновістю, тоном та змістом запиту.

- "short_summary" — коротко опиши суть запиту одним реченням.

- "requested_actions" — список конкретних дій, які очікує замовник.
  Якщо конкретних дій немає — порожній список.

- "needs_clarification" — true, якщо запит недостатньо конкретний
  для початку роботи. Інакше false.

Не додавай жодних пояснень поза JSON.

Приклад формату відповіді:

{{
  "category": "автоматизація",
  "target_department": "маркетинг",
  "priority": "medium",
  "short_summary": "Автоматизувати щотижневий збір та формування звіту по Google Ads.",
  "requested_actions": [
    "отримувати дані Google Ads",
    "формувати звіт по основних метриках кампаній"
  ],
  "needs_clarification": false
}}
"""

    return llm.invoke(prompt)