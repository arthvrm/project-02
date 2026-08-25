import logging

from langchain_ollama import OllamaLLM
from pydantic import ValidationError

from app.models import RequestClassification


class RequestClassifier:
    def __init__(
        self,
        model_name: str,
        max_retries: int,
        logger: logging.Logger,
    ) -> None:
        self.llm = OllamaLLM(model=model_name)
        self.max_retries = max_retries
        self.logger = logger

    def classify(
        self,
        request_text: str,
    ) -> RequestClassification | None:
        prompt = self._build_prompt(request_text)

        for attempt in range(1, self.max_retries + 1):
            self.logger.info(
                "LLM classification attempt %d/%d",
                attempt,
                self.max_retries,
            )

            raw_response = self.llm.invoke(prompt)

            try:
                result = RequestClassification.model_validate_json(
                    raw_response
                )

                self.logger.info(
                    "LLM response validated successfully"
                )

                return result

            except ValidationError as exc:
                self.logger.warning(
                    "LLM response validation failed "
                    "on attempt %d/%d: %s",
                    attempt,
                    self.max_retries,
                    exc,
                )

                if attempt == self.max_retries:
                    self.logger.error(
                        "All LLM classification attempts failed"
                    )

        return None

    @staticmethod
    def _build_prompt(request_text: str) -> str:
        return f"""
You are an AI request classifier for an internal AI solutions team.

Your task is to analyze an internal request and return a structured
classification.

Return ONLY valid JSON. Do not include Markdown, explanations,
comments, or any text outside the JSON object.

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
  The user asks for information, an opinion, or a theoretical
  explanation without requesting implementation.

- "поза скоупом":
  The request is outside the responsibilities of an AI solutions
  team or is unrelated to the supported scope.

Priority guidelines:

- "high":
  Explicit urgency, critical business impact, or an immediate
  deadline.

- "medium":
  A concrete business request without critical urgency.

- "low":
  Informational requests, ideas, non-urgent improvements,
  or requests without a clear deadline.

Important rules:

1. "target_department" must contain the requesting department
   if it can be inferred from the request. Otherwise use null.

2. "short_summary" must contain exactly one concise sentence.

3. "requested_actions" must contain only concrete actions
   requested by the user.

4. "needs_clarification" must be true if the request is too vague
   to start implementation without additional information.

5. Do not invent information that is not present in the request.

6. Do not add fields that are not specified in the schema.

Examples:

Example 1:

Request:
"Can you automate our weekly Google Ads report? We currently
export CSV manually every Monday and copy the data into a sheet."

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

Example 2:

Request:
"URGENT. We need to export all contractors with expenses over
50k for May today. Accounting needs it immediately."

Output:
{{
    "category": "звіт/аналітика",
    "target_department": "accounting",
    "priority": "high",
    "short_summary": "Export contractors whose May expenses exceed 50k.",
    "requested_actions": [
        "filter contractors by May expenses",
        "export the matching contractors"
    ],
    "needs_clarification": false
}}

Example 3:

Request:
"Guys, we need a bot."

Output:
{{
    "category": "автоматизація",
    "target_department": null,
    "priority": "medium",
    "short_summary": "Create a bot.",
    "requested_actions": [
        "create a bot"
    ],
    "needs_clarification": true
}}

Now classify this request:

---
{request_text}
---
"""