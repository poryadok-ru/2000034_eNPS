FROM python:3.10-slim-bullseye

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        wget \
        xz-utils \
        fontconfig \
        libxrender1 \
        libxtst6 \
        libjpeg62-turbo \
        libssl1.1 \
        libpng16-16 \
        libxcb1 \
        libx11-6 \
        libpq5 \
        && \
    wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb -O /tmp/wkhtmltox.deb && \
    apt-get install -y --no-install-recommends /tmp/wkhtmltox.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/wkhtmltox.deb

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ файлы проекта
COPY src/main.py .
COPY src/config/ ./src/config/
COPY src/database/ ./src/database/
COPY src/ai/ ./src/ai/
COPY src/reports/ ./src/reports/
COPY src/bitrix/ ./src/bitrix/
COPY src/utils/ ./src/utils/

# Создаем выходную директорию
RUN mkdir -p /app/output_reports

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "-u", "src/main.py"]