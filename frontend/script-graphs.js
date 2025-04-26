const data = {
    suspicious_meters: [
        {
            serial_number: "SN2023-ABC-123",
            reason: "Резкий скачок потребления в ночное время",
            suspicion_level: 0.95,
        },
        {
            serial_number: "SN2023-DEF-456",
            reason: "Постоянно высокое потребление",
            suspicion_level: 0.88,
        },
        {
            serial_number: "SN2024-GHI-789",
            reason: "Аномально высокий уровень реактивной энергии",
            suspicion_level: 0.92,
        },
    ],
    visualization_data: {
        "SN2023-ABC-123": {
            half_hour_readings_A_plus: [
                { timestamp: "2025-04-25T00:00:00", value: 1.2 },
                { timestamp: "2025-04-25T00:30:00", value: 1.5 },
                { timestamp: "2025-04-25T01:00:00", value: 4.8 },
                { timestamp: "2025-04-25T01:30:00", value: 4.5 },
                { timestamp: "2025-04-25T02:00:00", value: 4.9 },
                { timestamp: "2025-04-25T02:30:00", value: 1.3 },
                { timestamp: "2025-04-25T03:00:00", value: 1.1 },
            ],
            half_hour_readings_P_plus: [
                { timestamp: "2025-04-25T00:00:00", value: 0.2 },
                { timestamp: "2025-04-25T00:30:00", value: 0.3 },
                { timestamp: "2025-04-25T01:00:00", value: 0.8 },
                { timestamp: "2025-04-25T01:30:00", value: 0.7 },
                { timestamp: "2025-04-25T02:00:00", value: 0.9 },
                { timestamp: "2025-04-25T02:30:00", value: 0.2 },
                { timestamp: "2025-04-25T03:00:00", value: 0.1 },
            ],
            daily_readings_T0_A_plus: [
                { date: "2025-04-24", value: 25.6 },
                { date: "2025-04-25", value: 38.2 },
            ],
        },
        "SN2023-DEF-456": {
            half_hour_readings_A_plus: [
                { timestamp: "2025-04-25T00:00:00", value: 5.1 },
                { timestamp: "2025-04-25T00:30:00", value: 5.2 },
                { timestamp: "2025-04-25T01:00:00", value: 5.0 },
                { timestamp: "2025-04-25T01:30:00", value: 5.1 },
                { timestamp: "2025-04-25T02:00:00", value: 5.2 },
                { timestamp: "2025-04-25T02:30:00", value: 5.1 },
                { timestamp: "2025-04-25T03:00:00", value: 5.0 },
            ],
            half_hour_readings_P_plus: [
                { timestamp: "2025-04-25T00:00:00", value: 0.5 },
                { timestamp: "2025-04-25T00:30:00", value: 0.6 },
                { timestamp: "2025-04-25T01:00:00", value: 0.5 },
                { timestamp: "2025-04-25T01:30:00", value: 0.6 },
                { timestamp: "2025-04-25T02:00:00", value: 0.5 },
                { timestamp: "2025-04-25T02:30:00", value: 0.6 },
                { timestamp: "2025-04-25T03:00:00", value: 0.5 },
            ],
            daily_readings_T0_A_plus: [
                { date: "2025-04-24", value: 120.5 },
                { date: "2025-04-25", value: 122.1 },
            ],
        },
        "SN2024-GHI-789": {
            half_hour_readings_A_plus: [
                { timestamp: "2025-04-25T00:00:00", value: 0.8 },
                { timestamp: "2025-04-25T00:30:00", value: 0.9 },
                { timestamp: "2025-04-25T01:00:00", value: 0.7 },
                { timestamp: "2025-04-25T01:30:00", value: 0.8 },
                { timestamp: "2025-04-25T02:00:00", value: 0.9 },
                { timestamp: "2025-04-25T02:30:00", value: 0.7 },
                { timestamp: "2025-04-25T03:00:00", value: 0.8 },
            ],
            half_hour_readings_P_plus: [
                { timestamp: "2025-04-25T00:00:00", value: 3.2 },
                { timestamp: "2025-04-25T00:30:00", value: 3.5 },
                { timestamp: "2025-04-25T01:00:00", value: 3.3 },
                { timestamp: "2025-04-25T01:30:00", value: 3.4 },
                { timestamp: "2025-04-25T02:00:00", value: 3.6 },
                { timestamp: "2025-04-25T02:30:00", value: 3.3 },
                { timestamp: "2025-04-25T03:00:00", value: 3.5 },
            ],
            daily_readings_T0_A_plus: [
                { date: "2025-04-24", value: 15.1 },
                { date: "2025-04-25", value: 16.8 },
            ],
        },
    },
};

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

// Создаем список счетчиков
const metersList = document.getElementById("meters-list");

data.suspicious_meters.forEach((meter) => {
    const listItem = document.createElement("li");
    listItem.className = "meter-list-item";
    listItem.textContent = `${meter.serial_number} (Уровень подозрения: ${meter.suspicion_level})`;
    listItem.dataset.serialNumber = meter.serial_number;

    listItem.addEventListener("click", function () {
        // Удаляем активный класс у всех элементов
        document.querySelectorAll(".meter-list-item").forEach((item) => {
            item.classList.remove("active-meter");
        });

        // Добавляем активный класс текущему элементу
        this.classList.add("active-meter");

        // Показываем данные выбранного счетчика
        showMeterData(this.dataset.serialNumber);
    });

    metersList.appendChild(listItem);
});

// Функция для отображения данных счетчика
function showMeterData(serialNumber) {
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
            <span class="suspicion-level">Уровень подозрения: ${meter.suspicion_level}</span>
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

// Показываем первый счетчик по умолчанию
if (data.suspicious_meters.length > 0) {
    const firstMeter = document.querySelector(".meter-list-item");
    if (firstMeter) {
        firstMeter.classList.add("active-meter");
        showMeterData(data.suspicious_meters[0].serial_number);
    }
}
