import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Добавляем импорт
from main import generate_tests

app = FastAPI(title="api for tests")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://213.165.52.36",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_test_cases(file: UploadFile = File(...)):
    # Базовая проверка расширения
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате JSON")

    try:
        # Читаем файл в память
        content = await file.read()
        swagger_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Ошибка парсинга: Невалидный JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения файла: {str(e)}")

    # Передаем распаршенный словарь в бизнес-логику
    try:
        tests = generate_tests(swagger_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации тестов: {str(e)}")

    # Возвращаем в нужном для фронта формате
    return {
        "tests": tests
    }