import json

INPUT_FILE = "twilio-messaging.json"


def load_swagger(file_path)->dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_tests(swagger):
    if not(swagger):
        return []

    tests = []
    paths = swagger.get("paths", {})

    http_methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']

    for path, path_node in paths.items():
        path_level_params = path_node.get("parameters", []) if isinstance(path_node, dict) else []

        for method, info in path_node.items():
            if(method.lower() not in http_methods or not isinstance(info, dict)):
                continue

            method_upper = method.upper()
            summary = info.get("summary") or info.get("operationId") or f"{method_upper} {path}"

            method_params = info.get("parameters", [])
            all_params = path_level_params + method_params

            # разделение параметров по расположению
            parameters = info.get("parameters", [])
            path_params = [p.get("name") for p in all_params if isinstance(p, dict) and p.get("in") == "path"]
            query_params = [p.get("name") for p in all_params if isinstance(p, dict) and p.get("in") == "query"]

            has_body = "requestBody" in info

            responses = info.get("responses", {})

            # позитивные тесты
            success_codes = [code for code in responses if code.startswith("2")]

            target_success = success_codes[0] if success_codes else "200"
            succes_description = responses.get(target_success, {}).get("description", "Запрос выполнен успешно")
            pos_steps = []
            pos_steps.append(f"1. Отправить {method_upper} запрос на {path}")

            step = 2
            if path_params:
                pos_steps.append(f"{step}. Подставить валидные значения в путь: {', '.join(path_params)}")
                step += 1
            if query_params:
                pos_steps.append(f"{step}. Указать Query-параметры: {', '.join(query_params)}")
                step+=1
            if has_body:
                pos_steps.append(f"{step}. Передать корректное JSON-тело запроса")
                step+=1
            pos_test_text = (f"{summary}\n"
                             f"Endpoint: {method_upper} {path}\n"
                             f"Тип теста: Позитивный\n\n"
                             f"Шаги" + "\n".join(pos_steps) + "\n\n"
                             f"Ожидаемый результат:\n"
                             f"- Статус ответа: {target_success}\n"
                             f"- {succes_description}\n"
            )
            tests.append(pos_test_text)



            # негативные тесты
            negative_codes = [code for code in responses if code.startswith("4") or code.startswith("5")]

            # стандартный негативный код, если в сваггере их нет
            if not negative_codes:
                negative_codes = ["400"]


            for code in negative_codes:
                display_code = "400 (Bad Request)" if code == "4XX" else code
                error_description = responses.get(code, {}).get("description", "Возвращена ошибка валидации или сервера")
                negative_test_text = (
                    f"{summary}\n"
                    f"Endpoint: {method_upper} {path}\n"
                    f"Тип теста: Негативный ({display_code})\n"
                    f"Шаги:\n"
                    f"1. Отправить {method_upper} запрос на {path}\n"
                    f"2. Передать некорректные или пустые данные\n"
                    f"Ожидаемый результат:\n"
                    f"- Статус ответа: {code}\n"
                    f"- Сообщение об ошибке: {error_description}"
                )
                tests.append(negative_test_text)

    return tests



def get_json_response(file_path):

    swagger_data = load_swagger(file_path)

    if swagger_data is None:
        return json.dumps({"success": False, "tests": []}, ensure_ascii=False)

    try:
        tests = generate_tests(swagger_data)
        result = {
            "success": True,
            "tests": tests
        }
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "tests": []
        }

    return json.dumps(result, ensure_ascii=False, indent=4)

def main():

    swagger = load_swagger(INPUT_FILE)
    tests = generate_tests(swagger)

    print(get_json_response(INPUT_FILE))
    #print(generate_tests(swagger))

    print(f"Сгенерировано тестов: {len(tests)}")


if __name__ == "__main__":
    main()