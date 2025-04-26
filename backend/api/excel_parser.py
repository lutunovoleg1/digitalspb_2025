import pandas as pd
import warnings


warnings.simplefilter(action='ignore', category=FutureWarning)



def feel_nans(df: pd.DataFrame) -> pd.DataFrame:
    # Удаляем столбец a_minus
    df = df.drop(columns=['a_minus'])

    # Удаляем device_id, где a_plus содержит только NaN на протяжении всего времени или NaN более 3 дней подряд
    def filter_device_ids(device_df):
        device_df['time'] = pd.to_datetime(device_df['time'])
        device_df = device_df.sort_values(by='time')
        # Вычисляем последовательности NaN
        device_df['nan_streak'] = device_df['a_plus'].isna().astype(int).groupby(
            device_df['time'].diff().dt.days.ne(1).cumsum()
        ).cumsum()
        # Удаляем device_id, если все значения NaN или есть NaN более 3 дней подряд
        if device_df['a_plus'].isna().all() or device_df['nan_streak'].max() > 3:
            return None
        return device_df.drop(columns=['nan_streak'])

    # Применяем фильтрацию для каждой группы device_id
    df = df.groupby('device_id', group_keys=False).apply(filter_device_ids).dropna(how='all')

    # Обрабатываем пропущенные значения для каждого device_id отдельно
    def fill_device_nans(device_df):
        device_df = device_df.sort_values(by='time')
        # Линейная интерполяция с заполнением крайними значениями
        device_df = device_df.interpolate(method='linear', limit_direction='both')
        return device_df

    # Применяем обработку для каждой группы device_id
    df = df.groupby('device_id', group_keys=False).apply(fill_device_nans)

    return df


def parse_excel_to_list(file_content: str) -> pd.DataFrame:

    df = pd.read_excel(file_content, sheet_name=0, engine='calamine')
    df = df.where(pd.notna(df), None)

    column_headers = df.columns.tolist()

    dates = [column_headers[i] for i in range(3, len(column_headers), 4)]

    print(len(dates))

    readings_list = list()
    
    data_list = df.values.tolist()

    for i in range(1, len(data_list)):
        device_id = str(int(data_list[i][1]))
        for j in range(len(dates)):
            readings_list.append(
                {
                    'time': dates[j],
                    'device_id': device_id,
                    'a_plus': data_list[i][j * 4 + 3],
                    'a_minus': data_list[i][j * 4 + 4],
                    'r_plus': data_list[i][j * 4 + 5],
                    'r_minus': data_list[i][j * 4 + 6],
                }
            )

    df_parsed = pd.DataFrame(data = readings_list, columns = ['time', 'device_id', 'a_plus', 'a_minus', 'r_plus', 'r_minus'])

    df_processed = feel_nans(df_parsed)

    return df_processed.to_dict('records')