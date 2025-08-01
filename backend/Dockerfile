FROM python:3.11-slim

# Установка системных зависимостей (включая для Pillow + cron для отзывов)
RUN apt-get update && \
    apt-get install -y \
        gcc \
        libjpeg-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libopenjp2-7-dev \
        libtiff-dev \
        tk-dev \
        tcl-dev \
        libwebp-dev \
        gettext \
        cron \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей и установка Python-библиотек
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Компиляция переводов
RUN django-admin compilemessages

# Создание директории для логов отзывов
RUN mkdir -p /tmp && touch /tmp/reviews.log

# Запуск через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]
