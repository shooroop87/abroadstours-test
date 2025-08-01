# backend/blog/migrations/0001_initial.py
# Запустите эту команду для создания миграций:
# python manage.py makemigrations blog
# python manage.py migrate

# backend/blog/apps.py
from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Blog'

# backend/blog/__init__.py
default_app_config = 'blog.apps.BlogConfig'
