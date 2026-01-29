import json
import re
from collections import defaultdict
from datetime import datetime, timedelta

def parse_json_from_answers(answers):
    """Парсит JSON из поля answers"""
    if not answers:
        return {}

    if isinstance(answers, dict):
        return answers

    if isinstance(answers, str):
        try:
            # Пробуем распарсить как JSON
            return json.loads(answers)
        except json.JSONDecodeError:
            # Если не получается, пытаемся найти JSON в строке
            try:
                # Убираем возможные лишние символы
                cleaned = answers.strip()
                if cleaned.startswith('{') and cleaned.endswith('}'):
                    # Пробуем исправить возможные проблемы с кавычками
                    cleaned = cleaned.replace("'", '"')
                    return json.loads(cleaned)
            except:
                pass

    return {}

def extract_location_type_from_form_name(form_name):
    """Определяет тип подразделения строго по названию формы анкеты"""
    if not form_name:
        return "офис"
    fn = form_name.lower()
    if "склад" in fn:
        return "склад"
    if any(x in fn for x in ["розница", "магазин", "торгов", "тт"]):
        return "розница"
    if "офис" in fn:
        return "офис"

    return "офис"

def get_quarter_dates(dt=None, quarter_offset=0):
    if dt is None: dt = datetime.now()
    q = (dt.month - 1) // 3 + 1 + quarter_offset
    y = dt.year
    while q < 1: q += 4; y -= 1
    while q > 4: q -= 4; y += 1
    start = datetime(y, 1 + 3 * (q - 1), 1)
    if q == 4:
        end = datetime(y + 1, 1, 1) - timedelta(seconds=1)
    else:
        end = datetime(y, 1 + 3 * q, 1) - timedelta(seconds=1)
    return start, end

def get_quarter_number(dt):
    return ((dt.month - 1) // 3 + 1)

def get_rating_from_record(record):
    """Получает оценку ТОЛЬКО из поля rating. Если NULL - возвращает None."""
    rating = record.get('rating')

    # Если rating равен None или NULL
    if rating is None:
        return None

    # Пытаемся преобразовать в целое число
    try:
        return int(float(rating))
    except (ValueError, TypeError):
        return None

def enps_calc(ratings):
    valid = [r for r in ratings if r is not None]
    count = len(valid)
    if count == 0: return {'enps': 0, 'total': 0, 'promoters': 0, 'neutral': 0, 'detractors': 0}
    p = sum(1 for r in valid if r >= 9)
    n = sum(1 for r in valid if 7 <= r <= 8)
    d = sum(1 for r in valid if r <= 6)
    enps_val = round(((p / count) - (d / count)) * 100, 1)
    return {'enps': enps_val, 'total': count, 'promoters': p, 'neutral': n, 'detractors': d}

def get_stats_table(curr, prev):
    # Определяем изменение eNPS
    enps_change = curr['enps'] - prev['enps']
    change_symbol = "↑" if enps_change > 0 else "↓" if enps_change < 0 else "→"

    return (f"| Показатель | Тек. квартал | Пред. квартал | Изменение |\n"
            f"| :--- | :--- | :--- | :--- |\n"
            f"| **eNPS** | **{curr['enps']}** | {prev['enps']} | {change_symbol}{abs(enps_change):.1f} |\n"
            f"| Респондентов | {curr['total']} | {prev['total']} | {change_symbol}{curr['total'] - prev['total']} |\n"
            f"| Промоутеры | {curr['promoters']} | {prev['promoters']} | {change_symbol}{curr['promoters'] - prev['promoters']} |\n"
            f"| Нейтралы | {curr['neutral']} | {prev['neutral']} | {change_symbol}{curr['neutral'] - prev['neutral']} |\n"
            f"| Критики | {curr['detractors']} | {prev['detractors']} | {change_symbol}{curr['detractors'] - prev['detractors']} |")