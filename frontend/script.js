document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("upload__form-input");
    const fileList = document.getElementById("upload__file-list");
    const uploadForm = document.getElementById("upload__form");

    fileInput.addEventListener("change", () => {
        fileList.innerHTML = "";
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const fileItem = document.createElement("div");
            fileItem.className = "upload__file-item";
            fileItem.innerHTML = `
          <span>${file.name} (${formatBytes(file.size)})</span>
        `;
            fileList.appendChild(fileItem);
        }
    });

    uploadForm.addEventListener("submit", (e) => {
        e.preventDefault();

        if (fileInput.files.length === 0) {
            alert("Пожалуйста, выберите файл!");
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);

        fetch("http://192.168.137.1:8000/upload/", {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Ошибка загрузки: ${response.status}`);
                }
                return response.text();
            })
            .then((result) => {
                alert("Файл успешно загружен!");
                console.log(result);
            })
            .catch((error) => {
                console.error("Ошибка:", error);
                alert("Произошла ошибка при загрузке файла.");
            });
    });

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
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (!file.name.endsWith(".xls") && !file.name.endsWith(".xlsx")) {
                alert("Разрешены только файлы Excel (.xls, .xlsx)");
                return;
            }
            fileInput.files = files;
            fileInput.dispatchEvent(new Event("change"));
        }
    });
});
