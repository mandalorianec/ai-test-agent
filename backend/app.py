import json
import asyncio
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

TEST_IT_URL = "https://api.testit.software/api/v2/workItems"
TEST_IT_API_TOKEN = "UDlWRVhxa0hrYlFqekVtWWN4"

PROJECT_ID = "019ce25b-28d8-7ff0-b14f-0d2f51c7a953"
SECTION_ID = "51b0a836-ad1c-4ae5-843c-15ed160c98a8"

HEADERS = {
    "Authorization": f"Bearer {TEST_IT_API_TOKEN}",
    "Content-Type": "application/json"
}


def map_to_testit_format(test: dict) -> dict:
    return {
        "projectId": PROJECT_ID,
        "sectionId": SECTION_ID,
        "name": test["name"],
        "description": f"{test['endpoint']['method']} {test['endpoint']['path']}",
        "entityTypeName": "TestCases",
        "duration": 1000,
        "state": "NeedsWork",
        "priority": test.get("priority", "Medium"),
        "attributes": {},
        "tags": test.get("tags", []),
        "preconditionSteps": [
            {"action": p} for p in test.get("preconditions", [])
        ],
        "postconditionSteps": [
            {"action": p} for p in test.get("postconditions", [])
        ],
        "links": [],
        "steps": [
            {
                "action": step["action"],
                "expected": step["expected_result"]
            }
            for step in test.get("steps", [])
        ]
    }


async def send_to_testit(client: httpx.AsyncClient, test: dict):
    response = await client.post(
        TEST_IT_URL,
        json=test,
        headers=HEADERS
    )
    return {
        "status": response.status_code,
        "response": response.text
    }


@app.post("/generate")
async def generate_test_cases(file: UploadFile = File(...)):
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Файл должен быть JSON")

    try:
        content = await file.read()
        swagger_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Невалидный JSON")

    try:
        tests = generate_tests(swagger_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # преобразуем в формат Test IT
    testit_tests = [map_to_testit_format(t) for t in tests]

    # отправляем
    async with httpx.AsyncClient() as client:
        tasks = [
            send_to_testit(client, test)
            for test in testit_tests
        ]
        results = await asyncio.gather(*tasks)

    return {
        "generated": len(tests),
        "sent": results
    }