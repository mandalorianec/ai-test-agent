import json

INPUT_FILE = "petstore-local.json"


def load_swagger(file_path)->dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_positive_test_case(summary, method_upper, path, path_params, query_params, has_body, target_success, success_description):
    steps = []
    step_number = 1

    steps.append({
        "step_number": step_number,
        "action": f"Отправить {method_upper} запрос на endpoint {path}",
        "expected_result": "Запрос отправлен"
    })
    step_number += 1

    if path_params:
        steps.append({
            "step_number": step_number,
            "action": f"Подставить валидные значения в path-параметры: {', '.join(path_params)}",
            "expected_result": "Path-параметры заполнены корректно"
        })
        step_number += 1

    if query_params:
        steps.append({
            "step_number": step_number,
            "action": f"Указать валидные query-параметры: {', '.join(query_params)}",
            "expected_result": "Query-параметры заполнены корректно"
        })
        step_number += 1

    if has_body:
        steps.append({
            "step_number": step_number,
            "action": "Передать корректное JSON-тело запроса",
            "expected_result": "Тело запроса соответствует контракту API"
        })
        step_number += 1

    return {
        "name": f"{summary} — позитивный сценарий",
        "description": f"Проверка успешного выполнения запроса {method_upper} {path}",
        "preconditions": [
            "API доступно",
            "Пользователь авторизован, если endpoint требует авторизации",
            "Есть валидные тестовые данные для запроса"
        ],
        "postconditions": [
            "Система остается в консистентном состоянии"
        ],
        "priority": "Medium",
        "type": "Positive",
        "endpoint": {
            "method": method_upper,
            "path": path
        },
        "steps": steps,
        "expected_result": {
            "status_code": target_success,
            "message": success_description
        },
        "tags": ["api", "positive", method_upper.lower()],
        "metadata": {
            "has_body": has_body,
            "path_params": path_params,
            "query_params": query_params
        }
    }


def build_negative_test_case(summary, method_upper, path, code, error_description):
    display_code = "400 (Bad Request)" if code == "4XX" else code

    steps = [
        {
            "step_number": 1,
            "action": f"Отправить {method_upper} запрос на endpoint {path}",
            "expected_result": "Запрос отправлен"
        },
        {
            "step_number": 2,
            "action": "Передать некорректные, пустые или невалидные данные",
            "expected_result": "Сервис выполняет валидацию и отклоняет запрос"
        }
    ]

    return {
        "name": f"{summary} — негативный сценарий ({display_code})",
        "description": f"Проверка обработки ошибки для запроса {method_upper} {path}",
        "preconditions": [
            "API доступно",
            "Подготовлены невалидные или неполные входные данные"
        ],
        "postconditions": [
            "Некорректные данные не приводят к успешному изменению состояния системы"
        ],
        "priority": "Medium",
        "type": "Negative",
        "endpoint": {
            "method": method_upper,
            "path": path
        },
        "steps": steps,
        "expected_result": {
            "status_code": code,
            "message": error_description
        },
        "tags": ["api", "negative", method_upper.lower()],
        "metadata": {
            "error_code": code
        }
    }
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
            #parameters = info.get("parameters", [])
            path_params = [p.get("name") for p in all_params if isinstance(p, dict) and p.get("in") == "path"]
            query_params = [p.get("name") for p in all_params if isinstance(p, dict) and p.get("in") == "query"]

            has_body = "requestBody" in info

            responses = info.get("responses", {})

            # позитивные тесты
            success_codes = [code for code in responses if code.startswith("2")]

            target_success = success_codes[0] if success_codes else "200"
            succes_description = responses.get(target_success, {}).get("description", "Запрос выполнен успешно")

            positive_test = build_positive_test_case(
                summary=summary,
                method_upper=method_upper,
                path=path,
                path_params=path_params,
                query_params=query_params,
                has_body=has_body,
                target_success=target_success,
                success_description=succes_description
            )
            tests.append(positive_test)



            # негативные тесты
            negative_codes = [code for code in responses if code.startswith("4") or code.startswith("5")]

            if not negative_codes:
                negative_codes = ["400"]
            for code in negative_codes:
                error_description = responses.get(code, {}).get(
                    "description",
                    "Возвращена ошибка валидации или сервера"
                )
                negative_test = build_negative_test_case(
                    summary=summary,
                    method_upper=method_upper,
                    path=path,
                    code=code,
                    error_description=error_description
                )
                tests.append(negative_test)
    return tests



def get_json_response(file_path):
    swagger_data = load_swagger(file_path)

    if swagger_data is None:
        return json.dumps({"success": False, "tests": []}, ensure_ascii=False, indent=4)

    try:
        tests = generate_tests(swagger_data)
        result = {
            "success": True,
            "total_tests": len(tests),
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

    print(f"Сгенерировано тестов: {len(tests)}")


if __name__ == "__main__":
    main()