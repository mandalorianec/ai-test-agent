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

TEST_IT_URL = "https://team-a0ff.testit.software/api/v2/workItems"
TEST_IT_API_TOKEN = "UDlWRVhxa0hrYlFqekVtWWN4"

PROJECT_ID = "019ce25b-28d8-7ff0-b14f-0d2f51c7a953"
SECTION_ID = "f8351326-da10-4904-b0af-68ec347c1c36"

HEADERS = {
    "Authorization": f"PrivateToken {TEST_IT_API_TOKEN}",
    "Content-Type": "application/json"
}

MAX_CONCURRENT_REQUESTS = 5
RETRIES = 3
TIMEOUT = 30.0

semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


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
        "tags": [{"name": tag} for tag in test.get("tags", [])],
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
    for attempt in range(RETRIES):
        try:
            async with semaphore:
                response = await client.post(
                    TEST_IT_URL,
                    json=test,
                    headers=HEADERS
                )

            return {
                "status": response.status_code,
                "name": test["name"],
                "response": response.text
            }

        except httpx.PoolTimeout:
            if attempt < RETRIES - 1:
                await asyncio.sleep(1 * (attempt + 1))
                continue
            return {
                "status": "error",
                "name": test["name"],
                "response": "PoolTimeout"
            }

        except Exception as e:
            if attempt < RETRIES - 1:
                await asyncio.sleep(1 * (attempt + 1))
                continue
            return {
                "status": "error",
                "name": test["name"],
                "response": str(e)
            }


async def send_all_tests(testit_tests: list):
    limits = httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5
    )

    async with httpx.AsyncClient(
            timeout=TIMEOUT,
            limits=limits
    ) as client:
        tasks = [
            send_to_testit(client, test)
            for test in testit_tests
        ]

        results = await asyncio.gather(*tasks)

    return results


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

    testit_tests = [map_to_testit_format(t) for t in tests]

    results = await send_all_tests(testit_tests)

    success = sum(1 for r in results if r["status"] == 200)

    return {"created": len(tests),
            "success": success}
