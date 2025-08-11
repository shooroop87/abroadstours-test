#!/bin/bash

# Универсальный скрипт для исправления блога Django
echo "🚀 УНИВЕРСАЛЬНЫЙ СКРИПТ ИСПРАВЛЕНИЯ БЛОГА"
echo "========================================="

# Функция для определения среды
detect_environment() {
    if [ -f "docker-compose.yml" ] && command -v docker-compose &> /dev/null; then
        echo "docker"
    elif [ -f "manage.py" ] || [ -f "backend/manage.py" ]; then
        echo "local"
    else
        echo "unknown"
    fi
}

# Определяем среду
ENV=$(detect_environment)

echo "🔍 Обнаружена среда: $ENV"
echo ""

case $ENV in
    "docker")
        echo "🐳 Запускаем Docker версию..."
        if [ -f "fix_blog_docker.sh" ]; then
            chmod +x fix_blog_docker.sh
            ./fix_blog_docker.sh
        else
            echo "❌ fix_blog_docker.sh не найден!"
            echo "💡 Создайте файл fix_blog_docker.sh с Docker командами"
        fi
        ;;
    "local")
        echo "🖥️ Запускаем локальную версию..."
        if [ -f "fix_blog_local.sh" ]; then
            chmod +x fix_blog_local.sh
            ./fix_blog_local.sh
        else
            echo "❌ fix_blog_local.sh не найден!"
            echo "💡 Создайте файл fix_blog_local.sh с локальными командами"
        fi
        ;;
    "unknown")
        echo "❌ Неизвестная среда!"
        echo ""
        echo "📋 Создайте один из файлов:"
        echo "   - docker-compose.yml (для Docker)"
        echo "   - manage.py (для локальной разработки)"
        echo ""
        echo "🔧 Или запустите напрямую:"
        echo "   ./fix_blog_local.sh   (для локальной разработки)"
        echo "   ./fix_blog_docker.sh  (для Docker)"
        exit 1
        ;;
esac

echo ""
echo "✅ Скрипт завершен!"