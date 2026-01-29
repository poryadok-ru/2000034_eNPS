import uuid
from datetime import datetime
from pathlib import Path
from bitrix24_sdk import BitrixClient

def upload_to_bitrix(pdf_path: str, folder_name: str, file_name: str,
                    bitrix_token: str, bitrix_user_id: int,
                    bitrix_enps_reports_folder_id: int, is_company: bool = False) -> str:
    """
    Загрузить PDF отчет в Bitrix24 и вернуть публичную ссылку.
    """
    try:
        if not bitrix_token or not bitrix_user_id:
            return ""

        client = BitrixClient(token=bitrix_token, user_id=bitrix_user_id)

        # Определяем целевую папку в зависимости от типа отчета
        if is_company:
            target_folder_name = "Отчёты по компании"
        else:
            target_folder_name = folder_name

        target_folder_id = None

        # Ищем существующую папку
        try:
            children = client.disk.get_children(id=bitrix_enps_reports_folder_id)
            for item in children.result:
                if item.name == target_folder_name and item.type == "folder":
                    target_folder_id = item.id
                    break
        except Exception:
            pass

        # Создаем папку, если она не существует
        if target_folder_id is None:
            try:
                new_folder = client.disk.add_subfolder(
                    bitrix_enps_reports_folder_id,
                    {"NAME": target_folder_name}
                )
                target_folder_id = new_folder.result.id
            except Exception:
                return ""

        # Читаем файл
        with open(pdf_path, "rb") as f:
            file_content = f.read()

        # Генерируем уникальное имя файла с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = Path(pdf_path).suffix
        file_base_name = Path(pdf_path).stem
        unique_file_name = f"{file_base_name}_{timestamp}_{unique_id}{file_extension}"

        # Загружаем файл
        upload_result = client.disk.upload_file_complete(
            folder_id=target_folder_id,
            file_content=file_content,
            file_name=unique_file_name
        )

        # Получаем ссылку для скачивания
        download_url = getattr(
            upload_result.result,
            'download_url',
            getattr(
                upload_result.result, 'url',
                f"https://bitrix24.com/disk/downloadFile/{upload_result.result.id}/"
            )
        )
        return download_url

    except Exception:
        return ""

def upload_excel_to_bitrix(excel_path: str, folder_name: str, file_name: str,
                          bitrix_token: str, bitrix_user_id: int,
                          bitrix_enps_reports_folder_id: int, is_company: bool = False) -> str:
    """
    Загрузить Excel файл в Bitrix24 и вернуть публичную ссылку.
    """
    try:
        if not bitrix_token or not bitrix_user_id:
            return ""

        client = BitrixClient(token=bitrix_token, user_id=bitrix_user_id)

        # Определяем целевую папку в зависимости от типа отчета
        if is_company:
            target_folder_name = "Отчёты по компании"
        else:
            target_folder_name = folder_name

        target_folder_id = None

        # Ищем существующую папку
        try:
            children = client.disk.get_children(id=bitrix_enps_reports_folder_id)
            for item in children.result:
                if item.name == target_folder_name and item.type == "folder":
                    target_folder_id = item.id
                    break
        except Exception:
            pass

        # Создаем папку, если она не существует
        if target_folder_id is None:
            try:
                new_folder = client.disk.add_subfolder(
                    bitrix_enps_reports_folder_id,
                    {"NAME": target_folder_name}
                )
                target_folder_id = new_folder.result.id
            except Exception:
                return ""

        # Читаем файл
        with open(excel_path, "rb") as f:
            file_content = f.read()

        # Генерируем уникальное имя файла с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = Path(excel_path).suffix
        file_base_name = Path(excel_path).stem
        unique_file_name = f"{file_base_name}_{timestamp}_{unique_id}{file_extension}"

        # Загружаем файл
        upload_result = client.disk.upload_file_complete(
            folder_id=target_folder_id,
            file_content=file_content,
            file_name=unique_file_name
        )

        # Получаем ссылку для скачивания
        download_url = getattr(
            upload_result.result,
            'download_url',
            getattr(
                upload_result.result, 'url',
                f"https://bitrix24.com/disk/downloadFile/{upload_result.result.id}/"
            )
        )
        return download_url

    except Exception:
        return ""