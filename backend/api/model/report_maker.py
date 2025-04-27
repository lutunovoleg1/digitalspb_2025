from api.schemas import Report, SuspiciousMeter, HalfHourReading, DailyReading, VisualizationData
import pandas as pd


def make_report(df, predicted_criminals):

    suspicious_meters = [
        SuspiciousMeter(
            serial_number=str(elem),
            reason='miner',
            suspicion_level= 1.0
        )
        for elem in predicted_criminals
    ]

    print(len(suspicious_meters))

    if not pd.api.types.is_datetime64_any_dtype(df['time']):
        df['time'] = pd.to_datetime(df['time'])

    # Добавляем колонку date для агрегации по дням
    df['date'] = df['time'].dt.date

    visualization_data: Dict[str, VisualizationData] = {}

    # Уникальные устройства
    devices = df['device_id'].unique()

    for device in devices:
        device_df = df[df['device_id'] == device]

        # Получасовые показания a_plus и r_plus (по времени)
        half_hour_a_plus = [
            HalfHourReading(timestamp=ts, value=float(val))  # float для сериализации
            for ts, val in zip(device_df['time'], device_df['a_plus'])
            if pd.notnull(val)
        ]

        half_hour_p_plus = [
            HalfHourReading(timestamp=ts, value=float(val))
            for ts, val in zip(device_df['time'], device_df['r_plus'])
            if pd.notnull(val)
        ]

        # Средние дневные значения a_plus
        daily_a_plus = device_df.groupby('date')['a_plus'].mean().reset_index()
        daily_readings_t0_a_plus = [
            DailyReading(date=d, value=float(v))
            for d, v in zip(daily_a_plus['date'], daily_a_plus['a_plus'])
            if pd.notnull(v)
        ]

        visualization_data[device] = VisualizationData(
            half_hour_readings_A_plus=half_hour_a_plus,
            half_hour_readings_P_plus=half_hour_p_plus,
            daily_readings_T0_A_plus=daily_readings_t0_a_plus
        )

    report = Report(
        suspicious_meters=suspicious_meters,
        visualization_data=visualization_data
    )

    return report