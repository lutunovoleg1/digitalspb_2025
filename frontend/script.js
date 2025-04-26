document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("upload__form-input");
    const fileList = document.getElementById("upload__file-list");
    const uploadForm = document.getElementById("upload__form");

    // Обработка выбора файлов
    fileInput.addEventListener("change", () => {
        fileList.innerHTML = ""; // Очищаем список перед обновлением
        if (fileInput.files.length > 0) {
            Array.from(fileInput.files).forEach((file, index) => {
                const fileItem = document.createElement("div");
                fileItem.className = "upload__file-item";
                fileItem.innerHTML = `
                    <span>${file.name} (${formatBytes(file.size)})</span>
                    <span class="upload__file-remove-btn" data-index="${index}">×</span>
                `;
                fileList.appendChild(fileItem);
            });

            // Удаление файла из списка
            document.querySelectorAll(".upload__file-remove-btn").forEach((btn) => {
                btn.addEventListener("click", (e) => {
                    const index = e.target.getAttribute("data-index");
                    removeFileFromList(index);
                });
            });
        }
    });

    // Отправка формы (заглушка)
    uploadForm.addEventListener("submit", (e) => {
        e.preventDefault();
        if (fileInput.files.length === 0) {
            alert("Пожалуйста, выберите файлы!");
            return;
        }
        alert("Файлы отправлены на сервер! (здесь должна быть AJAX-загрузка)");
        // Реальная отправка через Fetch API или XMLHttpRequest
    });

    // Удаление файла из списка
    function removeFileFromList(index) {
        const files = Array.from(fileInput.files);
        files.splice(index, 1);

        // Создаем новый FileList (через DataTransfer)
        const dataTransfer = new DataTransfer();
        files.forEach((file) => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;

        // Обновляем список
        fileInput.dispatchEvent(new Event("change"));
    }

    // Форматирование размера файла
    function formatBytes(bytes) {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }

    const dropArea = document.querySelector(".upload");

    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.style.border = "none";
        fileInput.files = e.dataTransfer.files;
        fileInput.dispatchEvent(new Event("change"));
    });
});
