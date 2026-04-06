import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from openai import APIError, OpenAI, RateLimitError

from main import generate_tests

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

EDITABLE_FIELDS = ["name", "description", "preconditions", "steps", "postconditions"]
DEFAULT_MAX_RETRIES = 4
DEFAULT_RETRY_DELAY_SECONDS = 2

SYSTEM_PROMPT = """
Ты QA-инженер.
Твоя задача — улучшать автосгенерированные тест-кейсы API, делая их более человекочитаемыми.

Правила:
1. Не меняй смысл.
2. Не добавляй новые шаги.
3. Не удаляй уже указанные проверки.
4. Не меняй структуру JSON.
5. Можно изменять только:
   - name
   - description
   - preconditions
   - steps
   - postconditions
6. Нельзя изменять другие поля.
7. Верни только валидный JSON без markdown и без пояснений.
""".strip()


def _build_prompt(test_case: dict[str, Any]) -> str:
    return f"""
Улучшай читаемость тест-кейса и верни JSON той же структуры.

Исходный тест-кейс:
{json.dumps(test_case, ensure_ascii=False, indent=2)}
""".strip()


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return json.loads(text)


def _get_response_text(response) -> str:
    if not response.choices:
        raise ValueError("Qwen вернул пустой список choices")

    content = response.choices[0].message.content

    if content is None:
        return ""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            elif hasattr(item, "text") and item.text:
                parts.append(item.text)

        return "".join(parts).strip()

    return str(content).strip()


def merge_enhanced_test_case(
    original: dict[str, Any],
    enhanced: dict[str, Any],
) -> dict[str, Any]:
    result = dict(original)

    for field in EDITABLE_FIELDS:
        if field in enhanced:
            result[field] = enhanced[field]

    return result


def _create_chat_completion_with_retry(
    *,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float = 0.1,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay_seconds: int = DEFAULT_RETRY_DELAY_SECONDS,
):
    attempt = 0

    while True:
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                extra_body={
                    "reasoning": {
                        "enabled": False,
                        "exclude": True,
                    }
                },
            )
        except RateLimitError as error:
            attempt += 1

            if attempt > max_retries:
                raise

            wait_seconds = retry_delay_seconds * attempt
            print(
                f"[WARN] Rate limit для модели {model}. "
                f"Повтор {attempt}/{max_retries} через {wait_seconds} сек.: {error}"
            )
            time.sleep(wait_seconds)
        except APIError as error:
            status_code = getattr(error, "status_code", None)

            if status_code != 429:
                raise

            attempt += 1

            if attempt > max_retries:
                raise

            wait_seconds = retry_delay_seconds * attempt
            print(
                f"[WARN] API вернул 429 для модели {model}. "
                f"Повтор {attempt}/{max_retries} через {wait_seconds} сек.: {error}"
            )
            time.sleep(wait_seconds)


def enhance_test_case_with_ai(
    test_case: dict[str, Any],
    model: str = "qwen/qwen3.6-plus:free",
) -> dict[str, Any]:
    response = _create_chat_completion_with_retry(
        model=model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": _build_prompt(test_case),
            },
        ],
        temperature=0.1,
    )

    response_text = _get_response_text(response)

    if not response_text:
        raise ValueError("Qwen вернул пустой ответ")

    enhanced_raw = _extract_json(response_text)

    if not isinstance(enhanced_raw, dict):
        raise ValueError("Ответ Qwen не является JSON-объектом")

    return merge_enhanced_test_case(test_case, enhanced_raw)

'''
def debug_enhancer(
    swagger_path: str,
    limit: int = 3,
    model: str = "qwen/qwen3.6-plus:free",
) -> None:
    if not os.path.exists(swagger_path):
        raise FileNotFoundError(f"Swagger файл не найден: {swagger_path}")

    with open(swagger_path, "r", encoding="utf-8") as f:
        swagger = json.load(f)

    original_tests = generate_tests(swagger)

    if not original_tests:
        print("[INFO] generate_tests() не вернул тесты")
        return

    tests_for_debug = original_tests[:limit]

    print(f"[INFO] Всего сгенерировано тестов: {len(original_tests)}")
    print(f"[INFO] Для отладки выбрано: {len(tests_for_debug)}")
    print()

    for index, before in enumerate(tests_for_debug, start=1):
        try:
            after = enhance_test_case_with_ai(before, model=model)
        except Exception as e:
            print(f"[ERROR] Не удалось улучшить тест-кейс #{index}: {e}")
            after = before

        print("=" * 100)
        print(f"[TEST #{index}] BEFORE")
        print(json.dumps(before, ensure_ascii=False, indent=2))
        print()

        print(f"[TEST #{index}] AFTER")
        print(json.dumps(after, ensure_ascii=False, indent=2))
        print("=" * 100)
        print()


if __name__ == "__main__":
    SWAGGER_PATH = "petstore-local.json"
    DEBUG_LIMIT = 3

    debug_enhancer(
        swagger_path=SWAGGER_PATH,
        limit=DEBUG_LIMIT,
        model="qwen/qwen3.6-plus:free",
    )
'''