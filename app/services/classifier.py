from pydantic import ValidationError
from langchain_ollama import OllamaLLM

from app.models import RequestClassification


class RequestClassifier:
    def __init__(
        self,
        model_name: str = "qwen2.5:7b-instruct",
    ) -> None:
        self.llm = OllamaLLM(model=model_name)

    def classify(
        self,
        request_text: str,
    ) -> RequestClassification | None:
        prompt = self._build_prompt(request_text)

        raw_response = self.llm.invoke(prompt)

        try:
            return RequestClassification.model_validate_json(
                raw_response
            )
        except ValidationError as exc:
            print(f"Failed to validate LLM response: {exc}")
            print(f"Raw LLM response: {raw_response}")

            return None

    @staticmethod
    def _build_prompt(request_text: str) -> str:
        return f"""
You are an AI request classifier for an internal AI solutions team.

Analyze the following internal request:

---
{request_text}
---

Return ONLY valid JSON. Do not include Markdown,
explanations, comments, or any text outside the JSON object.

The JSON must contain exactly these fields:

{{
    "category": string,
    "target_department": string | null,
    "priority": string,
    "short_summary": string,
    "requested_actions": string[],
    "needs_clarification": boolean
}}

Rules:

1. "category" must be exactly one of:
   - "автоматизація"
   - "інтеграція"
   - "звіт/аналітика"
   - "баг/підтримка"
   - "питання/консультація"
   - "поза скоупом"

2. "target_department" is the department that requested
   the task. If the department cannot be determined,
   use null.

3. "priority" must be exactly one of:
   - "low"
   - "medium"
   - "high"

   Determine priority from urgency, tone, deadlines,
   and business impact.

4. "short_summary" must describe the essence of the
   request in one concise sentence.

5. "requested_actions" must contain the concrete actions
   requested by the user. It can contain zero, one,
   or multiple actions.

6. "needs_clarification" must be true if the request is
   too vague or lacks enough information to start working
   on it. Otherwise, use false.

Important:
- Do not invent information that is not present.
- If the department is unknown, use null.
- Do not add any fields that are not specified above.
"""