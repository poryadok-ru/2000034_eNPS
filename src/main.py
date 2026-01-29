import sys
from datetime import datetime
from collections import defaultdict

# Импорт из модулей проекта
from config.settings import *
from utils.logger import setup_logger
from database.db_handler import Database
from ai.analyzer import AIAnalyzer
from reports.pdf_generator import PDFGenerator
from reports.data_processor import *
from reports.excel_generator import create_excel_from_json_data
from bitrix.uploader import upload_to_bitrix, upload_excel_to_bitrix

# Инициализируем логгер глобально
logger = setup_logger(PORADOCK_TOKEN)

def main():
    logger.info(f"НАЧАЛО ГЕНЕРАЦИИ ОТЧЕТОВ eNPS\nВремя запуска: {datetime.now()}\n")
    try:
        db = Database(DB_CONFIG)
        ai = AIAnalyzer(LITELLM_CONFIG)

        q_start, q_end = get_quarter_dates(quarter_offset=-1)
        pq_start, pq_end = get_quarter_dates(quarter_offset=-2)
        year, q_num = q_start.year, get_quarter_number(q_start)

        # Получаем данные (уже отфильтрованные по rating IS NOT NULL)
        curr_data = db.fetch_submissions(q_start, q_end)
        prev_data = db.fetch_submissions(pq_start, pq_end)

        logger.info(f"Загружено записей: текущий квартал - {len(curr_data)}, предыдущий - {len(prev_data)}")

        excel_file = create_excel_from_json_data(curr_data, OUTPUT_DIR, year, q_num)

        if excel_file:
            # Загружаем Excel файл в Bitrix24 в ту же папку, что и отчет по компании
            logger.info(f"Excel файл успешно создан")
            excel_bitrix_url = upload_excel_to_bitrix(
                str(excel_file),
                "",
                f"00_JSON_данные_{year}Q{q_num}.xlsx",
                BITRIX_TOKEN,
                BITRIX_USER_ID,
                BITRIX_ENPS_REPORTS_FOLDER_ID,
                is_company=True
            )

            if excel_bitrix_url:
                logger.info(f"Excel файл успешно загружен в Bitrix24")
            else:
                logger.warning(f"Не удалось загрузить Excel файл в Bitrix24")
        else:
            logger.warning(f"Не удалось создать Excel файл")

        # Предварительная разметка данных по категориям
        for r in curr_data:
            r['l_type'] = extract_location_type_from_form_name(r['form_name'])
        for r in prev_data:
            r['l_type'] = extract_location_type_from_form_name(r['form_name'])

        # Собираем все оценки
        all_ratings = [get_rating_from_record(r) for r in curr_data]
        valid_ratings = [r for r in all_ratings if r is not None]

        # Счетчики для статистики
        total_reports = 0
        successful_bitrix_uploads = 0
        failed_bitrix_uploads = 0

        # 1. ОТЧЕТ ПО КОМПАНИИ
        # Получаем оценки для статистики
        curr_ratings = [get_rating_from_record(r) for r in curr_data]
        prev_ratings = [get_rating_from_record(r) for r in prev_data]

        c_stats = enps_calc(curr_ratings)
        c_prev_stats = enps_calc(prev_ratings)

        # Анализируем данные через ИИ
        c_ai_result = ai.analyze(curr_data, "Вся компания")

        md_company = f"""# Квартальный отчет eNPS: Вся компания
**Период:** {year}Q{q_num} ({q_start.strftime('%d.%m.%Y')} - {q_end.strftime('%d.%m.%Y')})  
**Дата создания:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

## 1. Общая статистика по компании
{get_stats_table(c_stats, c_prev_stats)}

## 2. Что нравится сотрудникам
{c_ai_result['positive_feedback']}

## 3. Что хотелось бы улучшить
{c_ai_result['negative_feedback']}

## 4. Общая аналитика
{c_ai_result['analytics']}

## 5. Рекомендации
{c_ai_result['recommendations']}

"""

        pdf_path = OUTPUT_DIR / f"00_Компания_отчет_{year}Q{q_num}.pdf"

        try:
            PDFGenerator.md_to_pdf(md_company, pdf_path, WKHTMLTOPDF_PATH)
            logger.info(f"Отчет сохранен: {pdf_path}")
            total_reports += 1
        except Exception as e:
            logger.error(f"Ошибка при создании PDF отчета компании: {e}")
            failed_bitrix_uploads += 1

        # Загружаем отчет по компании в Bitrix24
        bitrix_url = upload_to_bitrix(
            str(pdf_path),
            "",
            f"Компания_отчет_{year}Q{q_num}.pdf",
            BITRIX_TOKEN,
            BITRIX_USER_ID,
            BITRIX_ENPS_REPORTS_FOLDER_ID,
            is_company=True
        )

        if bitrix_url:
            successful_bitrix_uploads += 1
            logger.info(f"Отчёт по компании загружен в Bitrix24")
        else:
            failed_bitrix_uploads += 1
            logger.warning(f"Не удалось загрузить отчет компании в Bitrix24")

        # 2. ОТЧЕТЫ ПО ПОДРАЗДЕЛЕНИЯМ

        # Группируем по филиалу и отделу
        curr_groups = defaultdict(list)
        for r in curr_data:
            key = (r['filiation'] or "Не указано", r['department'] or "Не указано")
            curr_groups[key].append(r)

        prev_groups = defaultdict(list)
        for r in prev_data:
            key = (r['filiation'], r['department'])
            prev_groups[key].append(r)

        for (fil, dep), records in curr_groups.items():
            # Определяем тип подразделения
            l_type = records[0]['l_type']

            # Статистика по типу (все склады/офисы/розницы)
            type_records_curr = [r for r in curr_data if r['l_type'] == l_type]
            type_records_prev = [r for r in prev_data if r['l_type'] == l_type]

            l_curr_stats = enps_calc([get_rating_from_record(r) for r in type_records_curr])
            l_prev_stats = enps_calc([get_rating_from_record(r) for r in type_records_prev])

            # Статистика конкретного подразделения
            prev_records = prev_groups.get((fil, dep), [])
            u_curr_stats = enps_calc([get_rating_from_record(r) for r in records])
            u_prev_stats = enps_calc([get_rating_from_record(r) for r in prev_records])

            # Анализируем данные подразделения через ИИ
            u_ai_result = ai.analyze(records, f"{fil} / {dep}")

            md_unit = f"""# eNPS    отчет: {fil} / {dep}
**Квартал:** {year} Q{q_num} | **Категория:** {l_type}
**Период:** {q_start.strftime('%d.%m.%Y')} - {q_end.strftime('%d.%m.%Y')}
**Дата создания:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

## 1. Общая статистика({l_type}):
{get_stats_table(l_curr_stats, l_prev_stats)}

## 2. Статистика подразделения
{get_stats_table(u_curr_stats, u_prev_stats)}

## 3. Что нравится сотрудникам
{u_ai_result['positive_feedback']}

## 4. Что хотелось бы улучшить
{u_ai_result['negative_feedback']}

## 5. Общая аналитика
{u_ai_result['analytics']}

## 6. Рекомендации по развитию
{u_ai_result['recommendations']}

"""
            safe_fil = re.sub(r'[^\w\s-]', '', str(fil)).replace(" ", "_")
            safe_dep = re.sub(r'[^\w\s-]', '', str(dep)).replace(" ", "_")
            folder_name = f"{safe_fil}_{safe_dep}"
            fname = f"{safe_fil}_{safe_dep}_{l_type}_{year}Q{q_num}.pdf"

            try:
                PDFGenerator.md_to_pdf(md_unit, OUTPUT_DIR / fname, WKHTMLTOPDF_PATH)
                logger.info(f"Создан PDF: {fname}")
                total_reports += 1
            except Exception as e:
                logger.error(f"Ошибка при создании PDF {fname}: {e}")
                failed_bitrix_uploads += 1
                continue

            # Загружаем отчет подразделения в Bitrix24
            bitrix_url = upload_to_bitrix(
                str(OUTPUT_DIR / fname),
                folder_name,
                fname,
                BITRIX_TOKEN,
                BITRIX_USER_ID,
                BITRIX_ENPS_REPORTS_FOLDER_ID
            )

            if bitrix_url:
                successful_bitrix_uploads += 1
                logger.info(f"Отчёт {fname} загружен в Bitrix24")
            else:
                failed_bitrix_uploads += 1
                logger.warning(f"Не удалось загрузить отчет в Bitrix24")

        db.close()

        # Финальная статистика
        logger.info("ГЕНЕРАЦИЯ ОТЧЕТОВ ЗАВЕРШЕНА")
        logger.info(
            f"ИТОГОВАЯ СТАТИСТИКА:\n- Всего анкет в текущем квартале: {len(curr_data)}\n- Успешно извлечено оценок: {len(valid_ratings)}\n- eNPS компании: {c_stats['enps']}\n- Количество промоутеров (9-10): {c_stats['promoters']}\n- Количество нейтралов (7-8): {c_stats['neutral']}\n- Количество критиков (1-6): {c_stats['detractors']}\n- Всего создано отчетов: {total_reports}\n- Успешно загружено в Bitrix24: {successful_bitrix_uploads}\n- Не загружено в Bitrix24: {failed_bitrix_uploads}")

    except Exception as e:
        logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА В ОСНОВНОМ ПОТОКЕ: {e}")
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Прервано пользователем")
    except Exception as e:
        logger.critical(f"Необработанное исключение: {e}")
        sys.exit(1)