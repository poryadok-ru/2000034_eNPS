from log import Log

def setup_logger(poradock_token):
    """
    Настройка логгера.
    Возвращает объект логгера, совместимый с poradock-logging или стандартный.
    """
    if poradock_token:
        try:
            logger_instance = Log(token=poradock_token, silent_errors=True)
            return logger_instance
        except Exception:
            pass

    # Используем стандартный logging как fallback
    import logging

    # Создаем кастомный класс для совместимости
    class StandardLogger:
        def __init__(self):
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('enps_reports.log', encoding='utf-8')
                ]
            )
            self.logger = logging.getLogger('enps_reports')

        def debug(self, message):
            self.logger.debug(message)

        def info(self, message):
            self.logger.info(message)

        def warning(self, message):
            self.logger.warning(message)

        def error(self, message):
            self.logger.error(message)

        def critical(self, message):
            self.logger.critical(message)

        def exception(self, message):
            self.logger.exception(message)

    logger = StandardLogger()
    return logger