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

# Создание пользователя для безопасности ПЕРЕД созданием файлов
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Создание директорий для медиа файлов блога, логов и статики
RUN mkdir -p media/blog/featured media/blog/images media/uploads media/tours/featured media/tours/gallery && \
    mkdir -p logs && \
    mkdir -p core/static && \
    touch logs/reviews.log logs/django.log logs/tours.log

# Установка прав доступа для пользователя appuser
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod 666 logs/*.log

# Компиляция переводов
RUN django-admin compilemessages

# Переключение на пользователя appuser
USER appuser

# Запуск через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]
