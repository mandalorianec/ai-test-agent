import json

INPUT_FILE = "swagger.json"
OUTPUT_FILE = "test_cases.txt"


def load_swagger(file_path)->dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_tests(swagger):
    tests = []

    paths = swagger.get("paths", {})

    for path, methods in paths.items():
        for method, info in methods.items():

            summary = info.get("summary", f"{method.upper()} {path}")
            parameters = info.get("parameters", [])
            responses = info.get("responses", {})

            param_names = [p.get("name") for p in parameters]

            # валидные тесты
            success_codes = [code for code in responses if code.startswith("2")]

            test_text = f"### {summary}\n"
            test_text += f"Endpoint: {method.upper()} {path}\n"
            test_text += "Тип теста: Позитивный\n"
            test_text += "Шаги:\n"
            test_text += f"1. Отправить {method.upper()} запрос на {path}\n"

            if param_names:
                test_text += f"2. Передать параметры: {', '.join(param_names)}\n"
                step = 3
            else:
                step = 2

            if success_codes:
                test_text += f"{step}. Проверить статус ответа: {', '.join(success_codes)}\n"
            else:
                test_text += f"{step}. Проверить успешный ответ\n"

            test_text += f"{step+1}. Проверить корректность ответа\n"

            tests.append(test_text)

            # негативные тесты
            negative_codes = ["400", "401", "403", "404"]

            for code in negative_codes:
                if code in responses:

                    neg_test = f"### {summary}\n"
                    neg_test += f"Endpoint: {method.upper()} {path}\n"
                    neg_test += f"Тип теста: Негативный ({code})\n"
                    neg_test += "Шаги:\n"
                    neg_test += f"1. Отправить {method.upper()} запрос на {path} с некорректными данными\n"
                    neg_test += f"2. Проверить что статус ответа {code}\n"

                    tests.append(neg_test)

    return tests


def save_to_txt(tests, file_path):

    with open(file_path, "w", encoding="utf-8") as f:
        for test in tests:
            f.write(test)
            f.write("\n---------------------\n\n")


def main():

    swagger = load_swagger(INPUT_FILE)

    tests = generate_tests(swagger)

    save_to_txt(tests, OUTPUT_FILE)

    print(f"Сгенерировано тестов: {len(tests)}")
    print(f"Файл сохранён: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
