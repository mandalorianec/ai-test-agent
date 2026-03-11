'use strict'

const form = document.getElementById("upload-form")
const fileInput = document.getElementById("file-send")
const statusBlock = document.getElementById("status")
const resultsBlock = document.getElementById("results")


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