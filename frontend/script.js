'use strict'

const form = document.getElementById("upload-form")
const fileInput = document.getElementById("file-send")
const statusBlock = document.getElementById("status")


form.addEventListener("submit", async function (event) {
    event.preventDefault()

    //Получение файла
    const file = fileInput.files[0]

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

        const response = await fetch("http://213.165.52.36:8000/generate", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`)
        }

    } catch (error) {
        statusBlock.textContent = `Ошибка ${error.message}`
    }
})