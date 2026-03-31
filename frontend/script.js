'use strict';

const API_URL = 'http://213.165.52.36:8000/generate';

const form = document.getElementById('upload-form');
const fileInput = document.getElementById('file-send');
const fileName = document.getElementById('file-name');
const statusBlock = document.getElementById('status');

function setStatus(message, type = '') {
  statusBlock.textContent = message;
  statusBlock.classList.remove('status-box--success', 'status-box--error');

  if (type === 'success') {
    statusBlock.classList.add('status-box--success');
  }

  if (type === 'error') {
    statusBlock.classList.add('status-box--error');
  }
}

fileInput.addEventListener('change', () => {
  const selectedFile = fileInput.files[0];
  fileName.textContent = selectedFile ? selectedFile.name : 'Файл не выбран';
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const file = fileInput.files[0];

  if (!file) {
    setStatus('Выберите JSON-файл.', 'error');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('file', file);

    setStatus('Отправка файла на сервер...');

    const response = await fetch(API_URL, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Ошибка сервера: ${response.status}`);
    }

    setStatus('Файл успешно отправлен. Сервер принял запрос на генерацию тест-кейсов.', 'success');
  } catch (error) {
    setStatus(`Ошибка: ${error.message}`, 'error');
  }
});