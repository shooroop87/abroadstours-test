#!/bin/bash

# Скрипт для исправления настройки блога Django (DOCKER)
echo "🔧 Исправляем настройку блога Django (Docker)..."

# Проверяем наличие docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Ошибка: docker-compose.yml не найден!"
    echo "💡 Запустите скрипт из папки с docker-compose.yml"
    exit 1
fi

# 1. Останавливаем контейнеры
echo "⏹️ Останавливаем контейнеры..."
docker-compose down -v

# 2. Очищаем старые образы
echo "🧹 Очищаем кэш..."
docker-compose build --no-cache

# 3. Запускаем контейнеры
echo "🚀 Запускаем контейнеры..."
docker-compose up -d

# 4. Ждем пока база данных готова
echo "⏳ Ждем готовности базы данных..."
sleep 15

# 5. Диагностика блога (новая команда)
echo "🔍 Диагностика блога..."
docker-compose exec backend python manage.py diagnose_blog

# 6. Создаем миграции для blog приложения
echo "📁 Создаем миграции для blog..."
docker-compose exec backend python manage.py makemigrations blog

# 7. Применяем все миграции
echo "🔄 Применяем миграции..."
docker-compose exec backend python manage.py migrate

# 8. Проверяем статус миграций
echo "✅ Проверяем статус миграций..."
docker-compose exec backend python manage.py showmigrations

# 9. Повторная диагностика после миграций
echo "🔍 Повторная диагностика после миграций..."
docker-compose exec backend python manage.py diagnose_blog

# 10. Создаем суперпользователя (опционально)
echo "👤 Создаем суперпользователя для админки..."
docker-compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Суперпользователь создан: admin/admin123')
else:
    print('ℹ️ Суперпользователь уже существует')
"

# 11. Очищаем кэш Redis
echo "🗑️ Очищаем кэш Redis..."
docker-compose exec redis redis-cli FLUSHALL

# 12. Перезапускаем backend
echo "🔄 Перезапускаем backend..."
docker-compose restart backend

# Ждем после перезапуска
sleep 5

# 13. Проверяем логи
echo "📋 Проверяем логи..."
docker-compose logs --tail=30 backend

echo ""
echo "🎉 Готово! Попробуйте открыть:"
echo "   - http://localhost:8000/blog/ (список блога)"
echo "   - http://localhost:8000/admin/ (админка - admin/admin123)"
echo ""
echo "🔍 Если все еще есть ошибки, выполните:"
echo "   docker-compose logs -f backend"
echo ""
echo "📊 Для подробной диагностики:"
echo "   docker-compose exec backend python manage.py diagnose_blog"