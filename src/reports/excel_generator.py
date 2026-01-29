import pandas as pd
from pathlib import Path
from .data_processor import parse_json_from_answers, extract_location_type_from_form_name

def create_excel_from_json_data(data, output_path, year, q_num):
    """
    Создает Excel файл из данных JSON.
    Каждый столбец соответствует уникальному ключу JSON из поля answers.
    """

    if not data:
        return None

    all_keys = set()
    parsed_answers_list = []

    # Парсим все answers и собираем ключи
    for i, record in enumerate(data, 1):
        answers = record.get('answers')
        parsed = parse_json_from_answers(answers)
        parsed_answers_list.append(parsed)

        if parsed:
            all_keys.update(parsed.keys())


    if not all_keys:
        return None

    rows = []
    for i, (record, parsed_answers) in enumerate(zip(data, parsed_answers_list), 1):
        row = {}

        # Добавляем базовые поля из записи
        row['id'] = i
        row['form_name'] = record.get('form_name')
        row['filiation'] = record.get('filiation')
        row['department'] = record.get('department')
        row['rating'] = record.get('rating')
        row['l_type'] = extract_location_type_from_form_name(record.get('form_name', ''))

        # Добавляем все ключи JSON как столбцы
        for key in sorted(all_keys):
            row[key] = parsed_answers.get(key)

        rows.append(row)


    # Создаем DataFrame
    df = pd.DataFrame(rows)

    # Сортируем колонки: сначала базовые, потом JSON ключи
    base_columns = ['id', 'form_name', 'filiation', 'department', 'rating', 'l_type']
    # Оставляем только те базовые колонки, которые есть в DataFrame
    existing_base_columns = [col for col in base_columns if col in df.columns]
    json_columns = [col for col in sorted(all_keys) if col in df.columns]
    ordered_columns = existing_base_columns + json_columns

    # Переупорядочиваем колонки
    df = df[ordered_columns]

    # Создаем имя файла
    excel_path = output_path / f"00_Ответы_{year}Q{q_num}.xlsx"

    try:
        # Сохраняем в Excel - ТОЛЬКО ОДИН ЛИСТ
        df.to_excel(excel_path, sheet_name='Данные', index=False)
        return excel_path

    except Exception as e:
        raise e