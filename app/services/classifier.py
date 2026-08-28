import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from app.models import RequestClassification


class RequestClassifier:
    def __init__(self, model_name: str, max_retries: int, api_key: str, logger: logging.Logger) -> None:
        self.llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
        self.max_retries = max_retries
        self.logger = logger


    def classify(self, request_text: str) -> RequestClassification | None:
        prompt = self._build_prompt(request_text)

        for attempt in range(1, self.max_retries + 1):
            self.logger.info(
                "LLM classification attempt %d/%d",
                attempt,
                self.max_retries,
            )

            try:
                response = self.llm.invoke(prompt)
                raw_response = self._extract_text(response)
                
                return RequestClassification.model_validate_json(raw_response)

            except ValidationError as exc:
                self.logger.warning(
                    "LLM response validation failed "
                    "on attempt %d/%d: %s",
                    attempt,
                    self.max_retries,
                    exc,
                )

            except Exception:
                self.logger.exception(
                    "LLM request failed "
                    "on attempt %d/%d",
                    attempt,
                    self.max_retries,
                )

        self.logger.error("All LLM classification attempts failed")
        
        return None


    @staticmethod
    def _extract_text(response) -> str:
        content = response.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []

            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text")
                    if text:
                        text_parts.append(text)

            return "".join(text_parts)

        raise TypeError(
            f"Unsupported response content type: "
            f"{type(content).__name__}"
        )


    @staticmethod
    def _build_prompt(request_text: str) -> str:
        return f"""
You are an AI request classifier for an internal AI solutions team.

Analyze the following internal request.

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

Allowed categories:

- "автоматизація"
- "інтеграція"
- "звіт/аналітика"
- "баг/підтримка"
- "питання/консультація"
- "поза скоупом"

Allowed priorities:

- "low"
- "medium"
- "high"

Classification guidelines:

- "автоматизація":
  Automating a repetitive manual process.

- "інтеграція":
  Connecting two or more existing systems or services.

- "звіт/аналітика":
  Reporting, data analysis, dashboards, metrics,
  data aggregation, or anomaly detection.

- "баг/підтримка":
  An existing system, integration, or automation is broken
  or requires technical support.

- "питання/консультація":
  An informational, theoretical, or advisory question.

- "поза скоупом":
  A request outside the responsibilities of an AI solutions team.

Priority guidelines:

- "high":
  Explicit urgency, critical business impact,
  or an immediate deadline.

- "medium":
  A concrete business request without critical urgency.

- "low":
  Informational requests, ideas, or non-urgent improvements.

Important:

1. target_department must contain the requesting department
   if it can be determined. Otherwise use null.

2. short_summary must be exactly one concise sentence.

3. requested_actions must contain concrete requested actions.

4. needs_clarification must be true if the request is too vague
   to start implementation.

5. Do not invent information.

6. Do not add fields outside the schema.

Example:

Request:
"Can you automate our weekly Google Ads report? We currently
export CSV manually every Monday."

Output:
{{
    "category": "автоматизація",
    "target_department": "marketing",
    "priority": "medium",
    "short_summary": "Automate the weekly Google Ads reporting process.",
    "requested_actions": [
        "collect Google Ads campaign metrics",
        "generate a weekly report"
    ],
    "needs_clarification": false
}}

Now classify this request:

---
{request_text}
---
"""
