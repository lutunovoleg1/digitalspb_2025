import pandas as pd
import numpy as np
import joblib

import os

def load_model(model_path: str = None):
    if model_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'random_forest_model.pkl')
    model = joblib.load(model_path)
    return model

def predict_new_data(model, data: pd.DataFrame) -> np.ndarray:
    features = ['mean_a_plus', 'max_a_plus', 'std_a_plus', 'mean_r_plus', 'mean_r_minus']
    X = data[features].fillna(0)
    return model.predict(X)

def prepare_weekly_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Подготавливает агрегированные признаки по устройствам и неделям
    для последующего обучения классификатора.

    Args:
        df: исходный DataFrame с колонками 'device_id', 'time', 'a_plus', 'r_plus', 'r_minus'

    Returns:
        DataFrame с агрегированными признаками:
        ['device_id', 'week', 'mean_a_plus', 'max_a_plus', 'std_a_plus', 'mean_r_plus', 'mean_r_minus']
    """

    # Агрегируем признаки по device_id и неделям
    device_week_stats = df.groupby(['device_id']).agg(
        mean_a_plus=('a_plus', 'mean'),
        max_a_plus=('a_plus', 'max'),
        std_a_plus=('a_plus', 'std'),
        mean_r_plus=('r_plus', 'mean'),
        mean_r_minus=('r_minus', 'mean')
    ).reset_index()

    # Заполняем пропуски std_a_plus нулями (если есть группы с одним измерением)
    device_week_stats['std_a_plus'] = device_week_stats['std_a_plus'].fillna(0)

    return device_week_stats

def prediction(df: pd.DataFrame) -> list:
    """
    Основная функция для предсказания на новых данных.
    Возвращает список device_id, для которых модель предсказала подозрение (label=1).
    """
    # Загружаем модель
    model = load_model()

    # Подготавливаем данные (агрегируем по неделям)
    prepared_data = prepare_weekly_features(df)

    # Делаем предсказания
    predictions = predict_new_data(model, prepared_data)

    # Добавляем предсказания в DataFrame
    prepared_data['predictions'] = predictions

    # Фильтруем device_id с положительным предсказанием (например, 1)
    suspicious_devices = prepared_data.loc[prepared_data['predictions'] == 1, 'device_id'].unique()

    return suspicious_devices.tolist()
