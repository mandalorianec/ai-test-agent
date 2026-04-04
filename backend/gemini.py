import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai

from main import generate_tests

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


SYSTEM_PROMPT = """
Ты QA-инженер.
Твоя задача — улучшать автосгенерированные тест-кейсы API, делая их более человекочитаемыми и аккуратными.

Правила:
1. Не меняй смысл теста.
2. Не удаляй важные проверки.
3. Не придумывай новые шаги, которых не было.
4. Не меняй структуру JSON.
5. Можно изменять только поля:
   - name
   - description
   - preconditions
   - steps
   - postconditions
6. Нельзя изменять:
   - priority
   - tags
   - endpoint
   - metadata
7. Верни только валидный JSON без markdown и без пояснений.
"""


def _build_prompt(test_case: dict[str, Any]) -> str:
    return f"""
Улучши читаемость тест-кейса и верни JSON той же структуры.

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


def merge_enhanced_test_case(original: dict[str, Any], enhanced: dict[str, Any]) -> dict[str, Any]:
    result = dict(original)

    for field in ["name", "description", "preconditions", "steps", "postconditions"]:
        if field in enhanced:
            result[field] = enhanced[field]

    return result


def enhance_test_case_with_ai(
    test_case: dict[str, Any],
    model: str = "gemini-2.5-flash",
) -> dict[str, Any]:
    response = client.models.generate_content(
        model=model,
        contents=[
            SYSTEM_PROMPT,
            _build_prompt(test_case),
        ],
    )

    if not response.text:
        raise ValueError("Gemini вернул пустой ответ")

    enhanced_raw = _extract_json(response.text)

    if not isinstance(enhanced_raw, dict):
        raise ValueError("Ответ Gemini не является JSON-объектом")

    return merge_enhanced_test_case(test_case, enhanced_raw)


def enhance_test_cases_with_ai(
    test_cases: list[dict[str, Any]],
    model: str = "gemini-2.5-flash",
) -> list[dict[str, Any]]:
    enhanced_cases = []

    for index, test_case in enumerate(test_cases, start=1):
        try:
            enhanced = enhance_test_case_with_ai(test_case, model=model)
            enhanced_cases.append(enhanced)
            print(f"[OK] Улучшен тест-кейс #{index}: {enhanced.get('name', '')}")
        except Exception as e:
            print(f"[ERROR] Не удалось улучшить тест-кейс #{index}: {e}")
            enhanced_cases.append(test_case)

    return enhanced_cases

#откладка
"""
def debug_enhancer(
    swagger_path: str,
    limit: int = 2,
    model: str = "gemini-2.5-flash",
) -> None:
    '''
    Отладочный запуск:
    1. читает swagger из файла
    2. генерирует тесты через generate_tests()
    3. улучшает первые N тестов
    4. печатает BEFORE / AFTER
    '''
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

    for index, test_case in enumerate(tests_for_debug, start=1):
        print("=" * 100)
        print(f"[TEST #{index}] BEFORE")
        print(json.dumps(test_case, ensure_ascii=False, indent=2))
        print()

        try:
            enhanced = enhance_test_case_with_ai(test_case, model=model)
            print(f"[TEST #{index}] AFTER")
            print(json.dumps(enhanced, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"[TEST #{index}] ERROR: {e}")

        print("=" * 100)
        print()

if __name__ == "__main__":
    SWAGGER_PATH = "discord-api.json"
    DEBUG_LIMIT = 2

    debug_enhancer(
        swagger_path=SWAGGER_PATH,
        limit=DEBUG_LIMIT,
        model="gemini-2.5-flash",
    )
"""