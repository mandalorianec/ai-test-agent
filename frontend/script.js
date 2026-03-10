'use strict'

const form = document.getElementById("upload-form")
const fileInput = document.getElementById("file-send")
const statusBlock = document.getElementById("status")
const resultsBlock = document.getElementById("results")

// Тествый ответ
const USE_MOCK_RESPONSE = true;

form.addEventListener("submit", async function (event) {
    event.preventDefault()

    //Получение файла
    const file = fileInput.files[0]

    // Очищение старого результата
    resultsBlock.innerHTML = ""

    if (!file) {
        statusBlock.textContent = "Выберите JSON файл."
        return
    }

    statusBlock.textContent = "Файл выбран, пожалуйста подождите..."

    try {
        // Тестовый ответ
        if (USE_MOCK_RESPONSE) {
            statusBlock.textContent = "Обработка..."
            const mockData = {
               success: true,
                tests: [
                    "### Авторизация\nEndpoint: POST /login\nТип теста: Позитивный\nШаги:\n1. Отправить POST запрос на /login\n2. Передать корректные данные\n3. Проверить статус ответа: 200\n4. Проверить корректность ответа",
                    "### Получение пользователя\nEndpoint: GET /users/{id}\nТип теста: Негативный (404)\nШаги:\n1. Отправить GET запрос на /users/{id} с несуществующим id\n2. Проверить, что статус ответа 404"
                ] 
            }

            renderResults(mockData)
            return
        }

        // Запрос

        const formData = new FormData()
        formData.append("file", file)

        statusBlock.textContent = "Отправка файла на сервер..."

        const response = await fetch("http://localhost:5000/upload", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`)
        }

        const data = await response.json()
        renderResults(data)
    } catch (error) {
        statusBlock.textContent = `Ошибка ${error.message}`
        resultsBlock.innerHTML = ""
    }
})

function renderResults(data) {
    resultsBlock.innerHTML = ""

    if (!data.success) {
        statusBlock.textContent = "Сервер вернул ошибку."
        resultsBlock.textContent = data.error || "Не удалось получить тест-кейсы."
        return
    }

    if (!data.tests || data.tests.length === 0) {
        statusBlock.textContent = "Готово, но тест кейсы не найдены."
        resultsBlock.textContent = "Результат пуст."
        return
    }

    statusBlock.textContent = `Готово. Получено тест-кейсов: ${data.tests.length}`
    for (const test of data.tests) {
        const testBlock = document.createElement("pre")
        testBlock.classList.add("test-case")
        testBlock.textContent = test
        resultsBlock.appendChild(testBlock)
    }
}