# blog/management/commands/check_media.py
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Проверка медиа-файлов блога'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== ПРОВЕРКА НАСТРОЕК МЕДИА ==="))
        self.stdout.write(f"MEDIA_URL: {settings.MEDIA_URL}")
        self.stdout.write(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        
        media_exists = os.path.exists(settings.MEDIA_ROOT)
        self.stdout.write(f"MEDIA_ROOT существует: {'ДА' if media_exists else 'НЕТ'}")
        
        if not media_exists:
            self.stdout.write(self.style.WARNING(f"Создаю директорию: {settings.MEDIA_ROOT}"))
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        
        # Проверяем/создаем директории для блога
        blog_dirs = [
            Path(settings.MEDIA_ROOT) / 'blog',
            Path(settings.MEDIA_ROOT) / 'blog' / 'featured',
            Path(settings.MEDIA_ROOT) / 'blog' / 'images',
            Path(settings.MEDIA_ROOT) / 'uploads',  # для CKEditor
        ]
        
        self.stdout.write(f"\n{self.style.SUCCESS('=== ПРОВЕРКА ДИРЕКТОРИЙ ===')}") 
        for dir_path in blog_dirs:
            exists = dir_path.exists()
            status = "EXISTS" if exists else "СОЗДАНА"
            
            if not exists:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.stdout.write(f"{dir_path}: {self.style.WARNING(status)}")
            else:
                self.stdout.write(f"{dir_path}: {self.style.SUCCESS(status)}")
        
        # Проверяем посты с изображениями
        self.stdout.write(f"\n{self.style.SUCCESS('=== ПРОВЕРКА ПОСТОВ С ИЗОБРАЖЕНИЯМИ ===')}") 
        posts_with_images = BlogPost.objects.exclude(featured_image='')
        
        if not posts_with_images.exists():
            self.stdout.write(self.style.WARNING("Нет постов с featured_image"))
            
            # Показываем все посты
            all_posts = BlogPost.objects.all()
            self.stdout.write(f"\nВсего постов в базе: {all_posts.count()}")
            
            for post in all_posts[:5]:  # показываем первые 5
                title = post.get_display_title()
                has_image = "ДА" if post.featured_image else "НЕТ"
                self.stdout.write(f"  {post.id}: {title} - изображение: {has_image}")
            
            return
        
        for post in posts_with_images:
            self.stdout.write(f"\n{self.style.HTTP_INFO('Пост:')} {post.get_display_title()}")
            self.stdout.write(f"  ID: {post.id}")
            self.stdout.write(f"  Image field: {post.featured_image}")
            
            if post.featured_image:
                self.stdout.write(f"  Image URL: {post.featured_image.url}")
                
                try:
                    file_path = post.featured_image.path
                    exists = os.path.exists(file_path)
                    self.stdout.write(f"  File path: {file_path}")
                    
                    if exists:
                        size = os.path.getsize(file_path)
                        self.stdout.write(f"  File exists: {self.style.SUCCESS('ДА')}")
                        self.stdout.write(f"  File size: {size} bytes")
                    else:
                        self.stdout.write(f"  File exists: {self.style.ERROR('НЕТ')}")
                        self.stdout.write(self.style.ERROR(f"  ФАЙЛ НЕ НАЙДЕН: {file_path}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Ошибка проверки файла: {e}"))
        
        self.stdout.write(f"\n{self.style.SUCCESS('=== ИТОГО ===')}") 
        self.stdout.write(f"Постов с изображениями: {posts_with_images.count()}")
        
        # Проверяем содержимое media директории
        media_path = Path(settings.MEDIA_ROOT)
        if media_path.exists():
            self.stdout.write(f"\n{self.style.SUCCESS('=== СОДЕРЖИМОЕ MEDIA ДИРЕКТОРИИ ===')}") 
            for item in media_path.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(media_path)
                    size = item.stat().st_size
                    self.stdout.write(f"  {relative_path} ({size} bytes)")
