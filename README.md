# Класифікація внутрішніх запитів

CLI pipeline читає внутрішні запити з CSV, класифікує їх через Google Gemini, перевіряє відповідь Pydantic-моделлю та формує JSON і Markdown-звіт. Успішні класифікації також додаються до Google Sheets.

## Структура

```text
app/
	main.py                 # точка входу pipeline
	models.py               # Pydantic-моделі та enum-значення
	google_sheets.py        # запис результатів у Google Sheets
	services/
		classifier.py         # виклик LLM і retry невалідних відповідей
		report.py             # генерація Markdown-звіту
	utils/
		config.py             # завантаження .env і значення за замовчуванням
		file_handler.py       # читання CSV і запис JSON
		logger.py             # консольний та файловий logging
inputs/input_requests.csv # приклад вхідних даних
results/                  # результати запуску
tests/                    # тести моделей і звіту
```

## Вимоги

- Python 3.12+
- API-ключ [Google Gemini](https://ai.google.dev/gemini-api/docs/api-key)
- Google Cloud service account із доступом до потрібної таблиці
- `uv` або `pip`

Встановлення через `uv`:

```bash
uv sync
```

Альтернатива через virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Налаштування

Створіть `.env` у корені проєкту:

```env
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-3.5-flash-lite
MAX_RETRIES=3
INPUT_FILE=inputs/input_requests.csv
OUTPUT_FILE=results/output.json
REPORT_FILE=results/report.md
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_WORKSHEET_NAME=Requests
```

`GEMINI_API_KEY`, `GOOGLE_CREDENTIALS_FILE` і `GOOGLE_SPREADSHEET_ID` потрібні для повного запуску. Значення за замовчуванням:

- `LLM_MODEL`: `gemini-3.5-flash-lite`
- `MAX_RETRIES`: `3`
- `INPUT_FILE`: `inputs/input_requests.csv`
- `OUTPUT_FILE`: `results/output.json`
- `REPORT_FILE`: `results/report.md`
- `GOOGLE_CREDENTIALS_FILE`: `credentials.json`
- `GOOGLE_WORKSHEET_NAME`: `Requests`

Файл `credentials.json` має містити credentials service account. Надайте email цього service account доступ до Google Spreadsheet і не публікуйте файл або API-ключ у репозиторії.

## Вхідні дані

CSV має містити обов'язкові колонки:

| Колонка | Опис |
|---|---|
| `id` | Унікальний ідентифікатор запиту |
| `channel` | Канал надходження, наприклад `Slack` або `Email` |
| `timestamp` | Дата й час у форматі, який розпізнає Pydantic |
| `raw_text` | Текст запиту, не порожній |

Приклад: `inputs/input_requests.csv`.

## Запуск

Після активації virtual environment:

```bash
python -m app.main
```

Pipeline:

1. Читає всі рядки з `INPUT_FILE`.
2. Для кожного запиту викликає LLM і повторює запит до `MAX_RETRIES` разів, якщо відповідь не проходить валідацію.
3. Записує успішні результати в `OUTPUT_FILE`.
4. Створює статистичний звіт у `REPORT_FILE`.
5. Додає результати до аркуша `GOOGLE_WORKSHEET_NAME`.

Якщо аркуша з такою назвою немає, він створюється автоматично. Для кожного рядка Google Sheets використовуються поля `ID`, `Category`, `Department`, `Priority`, `Summary`, `Requested Actions` і `Needs Clarification`.

Тести:

```bash
uv run pytest
```

або:

```bash
pytest
```

## Формат класифікації

Кожен успішний результат містить:

- `category`: `автоматизація`, `інтеграція`, `звіт/аналітика`, `баг/підтримка`, `питання/консультація` або `поза скоупом`;
- `target_department`: департамент або `null`;
- `priority`: `low`, `medium` або `high`;
- `short_summary`: короткий підсумок;
- `requested_actions`: список конкретних дій;
- `needs_clarification`: чи потрібні додаткові вимоги.

Невалідний JSON, зайві поля або неправильні значення відхиляються Pydantic. Якщо всі спроби завершилися невдало, запит потрапляє до секції `Failed Requests` у звіті й не додається до JSON та Google Sheets.

## Поточні обмеження

- CSV повністю завантажується в пам'ять, а запити обробляються послідовно.
- JSON і звіт зберігаються після завершення всієї обробки; checkpointing немає.
- Кожен запит виконує окремий LLM-виклик; немає кешування, batch-обробки, rate limiting або оцінки вартості.
- Валідація перевіряє структуру відповіді, але не фактичну якість класифікації.
- Помилка читання CSV або невалідний вхідний рядок може зупинити pipeline.
- Запис у Google Sheets виконується після локального збереження результатів, але помилка Sheets може завершити запуск із винятком.
- У `pyproject.toml` є `langchain-ollama`, але поточний класифікатор використовує `ChatGoogleGenerativeAI`; Ollama автоматично не підключається.

## Подальші покращення

1. Додати structured output і окрему обробку тимчасових помилок API.
2. Зберігати checkpoint після кожної успішної класифікації.
3. Додати потокову обробку CSV, rate limiting і контрольовану паралельність.
4. Додати кешування, підрахунок токенів, оцінку вартості та budget limit.
5. Додати evaluation-набір, regression-тести та версіонування промпта і моделі.
6. Посилити перевірку конфігурації та ізолювати помилки Google Sheets від локальних результатів.
