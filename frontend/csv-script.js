'use strict';

const XLSX_API_URL = 'http://213.165.52.36:8000/generate-xlsx';

const xlsxForm = document.getElementById('xlsx-upload-form');
const xlsxFileInput = document.getElementById('xlsx-file-send');
const xlsxFileNameLabel = document.getElementById('xlsx-file-name');
const xlsxStatusBlock = document.getElementById('xlsx-status');
const manualDownloadButton = document.getElementById('manual-download-btn');

let xlsxBlob = null;
let xlsxFileName = 'generated-file.xlsx';

function setXlsxStatus(message, type = '') {
  xlsxStatusBlock.textContent = message;
  xlsxStatusBlock.classList.remove('status-box--success', 'status-box--error');

  if (type === 'success') {
    xlsxStatusBlock.classList.add('status-box--success');
  }

  if (type === 'error') {
    xlsxStatusBlock.classList.add('status-box--error');
  }
}

function downloadBlobFile(blob, fileName) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();

  setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 1000);
}

xlsxFileInput.addEventListener('change', () => {
  const selectedFile = xlsxFileInput.files[0];
  xlsxFileNameLabel.textContent = selectedFile ? selectedFile.name : 'Файл не выбран';
});

xlsxForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const file = xlsxFileInput.files[0];

  if (!file) {
    setXlsxStatus('Выберите JSON-файл.', 'error');
    return;
  }

  manualDownloadButton.disabled = true;
  xlsxBlob = null;
  xlsxFileName = 'generated-file.xlsx';

  try {
    const formData = new FormData();
    formData.append('file', file);

    setXlsxStatus('Отправка файла на сервер...');

    const response = await fetch(XLSX_API_URL, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Ошибка сервера: ${response.status}`);
    }

    const responseBlob = await response.blob();
    xlsxBlob = responseBlob;

    const contentDisposition = response.headers.get('Content-Disposition');
    if (contentDisposition) {
      const match = contentDisposition.match(/filename\*?=(?:UTF-8''|")?([^";]+)/i);
      if (match && match[1]) {
        xlsxFileName = decodeURIComponent(match[1].replace(/"/g, '').trim());
      }
    }

    if (!xlsxFileName.toLowerCase().endsWith('.xlsx')) {
      xlsxFileName = 'generated-file.xlsx';
    }

    setXlsxStatus('Файл создан, скачивание сейчас начнётся...', 'success');
    manualDownloadButton.disabled = false;
    downloadBlobFile(xlsxBlob, xlsxFileName);
  } catch (error) {
    setXlsxStatus(`Ошибка: ${error.message}`, 'error');
  }
});

manualDownloadButton.addEventListener('click', () => {
  if (!xlsxBlob) {
    setXlsxStatus('Сначала создайте XLSX-файл.', 'error');
    return;
  }

  downloadBlobFile(xlsxBlob, xlsxFileName);
});