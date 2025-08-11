#!/bin/bash

# Скрипт для исправления блога Django (ЛОКАЛЬНАЯ РАЗРАБОТКА)
echo "🔧 Исправляем настройку блога Django (локально)..."

# Проверяем, что мы в правильной папке
if [ ! -f "manage.py" ] && [ ! -d "backend" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой папки проекта!"
    exit 1
fi

# Определяем путь к manage.py
if [ -f "manage.py" ]; then
    MANAGE_PY="python manage.py"
    PROJECT_ROOT="."
elif [ -f "backend/manage.py" ]; then
    MANAGE_PY="python backend/manage.py"
    PROJECT_ROOT="backend"
else
    echo "❌ Не найден manage.py!"
    exit 1
fi

echo "📍 Используем: $MANAGE_PY"
echo "📁 Корень проекта: $PROJECT_ROOT"

# 1. Проверяем Python окружение
echo "🐍 Проверяем Python окружение..."
python --version
pip list | grep -i django || echo "⚠️ Django не найден в окружении!"

# 2. Переходим в папку проекта
cd $PROJECT_ROOT

# 3. Диагностика блога (если команда существует)
echo "🔍 Диагностика блога..."
$MANAGE_PY diagnose_blog 2>/dev/null || echo "⚠️ Команда diagnose_blog еще не доступна"

# 4. Создаем миграции для blog приложения
echo "📁 Создаем миграции для blog..."
$MANAGE_PY makemigrations blog

# 5. Применяем все миграции
echo "🔄 Применяем миграции..."
$MANAGE_PY migrate

# 6. Проверяем статус миграций
echo "✅ Проверяем статус миграций..."
$MANAGE_PY showmigrations

# 7. Повторная диагностика после миграций
echo "🔍 Повторная диагностика после миграций..."
$MANAGE_PY diagnose_blog 2>/dev/null || echo "ℹ️ Диагностика пропущена"

# 8. Создаем суперпользователя (опционально)
echo "👤 Создаем суперпользователя для админки..."
$MANAGE_PY shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Суперпользователь создан: admin/admin123')
else:
    print('ℹ️ Суперпользователь уже существует')
" 2>/dev/null || echo "⚠️ Не удалось создать суперпользователя"

# 9. Собираем статические файлы
echo "📦 Собираем статические файлы..."
$MANAGE_PY collectstatic --noinput --clear

# 10. Проверяем настройки
echo "⚙️ Проверяем настройки..."
$MANAGE_PY check

echo ""
echo "🎉 Готово! Теперь запустите сервер разработки:"
echo "   cd $PROJECT_ROOT"
echo "   python manage.py runserver"
echo ""
echo "🌐 Затем откройте:"
echo "   - http://localhost:8000/blog/ (список блога)"
echo "   - http://localhost:8000/admin/ (админка - admin/admin123)"
echo ""
echo "🔍 Для диагностики:"
echo "   python manage.py diagnose_blog"