async function loadData() {
    // Настройки запроса с таймаутом
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000); // Таймаут 8 секунд

    try {
        const response = await fetch("http://192.168.137.1:8000/report/", {
            signal: controller.signal,
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
        });

        clearTimeout(timeoutId); // Отменяем таймаут, если запрос успешен

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Ошибка загрузки данных:", error);

        // Возвращаем тестовые данные только при определенных ошибках
        if (error.name === "AbortError" || error.message.includes("Failed to fetch")) {
            return getFallbackData();
        } else {
            throw error; // Перебрасываем другие ошибки
        }
    }
}

// Тестовые данные вынесены в отдельную функцию
function getFallbackData() {
    return {
        suspicious_meters: [
            {
                serial_number: "SN-ERROR-001",
                reason: "Сервер недоступен. Используются тестовые данные.",
                suspicion_level: 0.99,
            },
        ],
        visualization_data: {
            "SN-ERROR-001": {
                half_hour_readings_A_plus: [
                    { timestamp: "2025-01-01T00:00:00", value: 1.5 },
                    { timestamp: "2025-01-01T00:30:00", value: 2.0 },
                ],
                half_hour_readings_P_plus: [
                    { timestamp: "2025-01-01T00:00:00", value: 0.3 },
                    { timestamp: "2025-01-01T00:30:00", value: 0.4 },
                ],
                daily_readings_T0_A_plus: [
                    { date: "2025-01-01", value: 10.0 },
                    { date: "2025-01-02", value: 15.0 },
                ],
            },
        },
    };
}

// Функция для форматирования времени
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// Функция для форматирования даты
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString();
}

// Функция для отображения данных счетчика
function showMeterData(data, serialNumber) {
    const metersContainer = document.getElementById("meters-container");
    metersContainer.innerHTML = "";

    const meter = data.suspicious_meters.find((m) => m.serial_number === serialNumber);
    const meterData = data.visualization_data[serialNumber];

    if (!meter || !meterData) return;

    // Создаем контейнер для счетчика
    const meterContainer = document.createElement("div");
    meterContainer.className = "meter-container";
    meterContainer.style.display = "block"; // Показываем контейнер
    meterContainer.innerHTML = `
        <h2>Счетчик: ${meter.serial_number}</h2>
        <div class="reason">
            <strong>Причина подозрения:</strong> ${meter.reason}
        </div>
        <div class="chart-container">
            <canvas id="${meter.serial_number}-hourly"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="${meter.serial_number}-daily"></canvas>
        </div>
    `;
    metersContainer.appendChild(meterContainer);

    // Подготавливаем данные для почасового графика
    const hourlyLabels = meterData.half_hour_readings_A_plus.map((r) => formatTime(r.timestamp));
    const aPlusData = meterData.half_hour_readings_A_plus.map((r) => r.value);
    const pPlusData = meterData.half_hour_readings_P_plus.map((r) => r.value);

    // Создаем почасовой график
    new Chart(document.getElementById(`${meter.serial_number}-hourly`), {
        type: "line",
        data: {
            labels: hourlyLabels,
            datasets: [
                {
                    label: "Активная энергия (A+)",
                    data: aPlusData,
                    borderColor: "rgb(75, 192, 192)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    tension: 0.1,
                    yAxisID: "y",
                },
                {
                    label: "Реактивная энергия (P+)",
                    data: pPlusData,
                    borderColor: "rgb(255, 99, 132)",
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    tension: 0.1,
                    yAxisID: "y1",
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: "linear",
                    display: true,
                    position: "left",
                    title: {
                        display: true,
                        text: "Активная энергия (A+)",
                    },
                },
                y1: {
                    type: "linear",
                    display: true,
                    position: "right",
                    title: {
                        display: true,
                        text: "Реактивная энергия (P+)",
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
            },
        },
    });

    // Подготавливаем данные для ежедневного графика
    const dailyLabels = meterData.daily_readings_T0_A_plus.map((r) => formatDate(r.date));
    const dailyData = meterData.daily_readings_T0_A_plus.map((r) => r.value);

    // Создаем ежедневный график
    new Chart(document.getElementById(`${meter.serial_number}-daily`), {
        type: "bar",
        data: {
            labels: dailyLabels,
            datasets: [
                {
                    label: "Ежедневное потребление (A+)",
                    data: dailyData,
                    backgroundColor: "rgba(54, 162, 235, 0.5)",
                    borderColor: "rgb(54, 162, 235)",
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Потребление (кВтч)",
                    },
                },
            },
        },
    });
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", async () => {
    const data = await loadData();
    if (!data) {
        alert("Данные не загружены. Проверьте подключение к серверу.");
        return;
    }

    const metersList = document.getElementById("meters-list");
    if (!metersList) return;

    // Заполнение списка счетчиков и построение графиков
    data.suspicious_meters.forEach((meter) => {
        const listItem = document.createElement("li");
        listItem.className = "meter-list-item";
        listItem.textContent = `${meter.serial_number}`;
        listItem.dataset.serialNumber = meter.serial_number;

        listItem.addEventListener("click", () => {
            document.querySelectorAll(".meter-list-item").forEach((item) => {
                item.classList.remove("active-meter");
            });
            listItem.classList.add("active-meter");
            showMeterData(data, meter.serial_number);
        });

        metersList.appendChild(listItem);
    });

    // Автовыбор первого счетчика
    if (data.suspicious_meters.length > 0) {
        showMeterData(data, data.suspicious_meters[0].serial_number);
        metersList.firstChild.classList.add("active-meter");
    }
});
