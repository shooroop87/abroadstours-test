# backend/blog/models.py
import logging
import os
import re
import traceback

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from easy_thumbnails.fields import ThumbnailerImageField
from parler.models import TranslatableModel, TranslatedFields
from taggit.managers import TaggableManager
from PIL import Image

# Настройка логгера
logger = logging.getLogger('blog.models')


class Category(TranslatableModel):
    """Категории блога с переводами"""
    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name="Name"),
        description=models.TextField(blank=True, verbose_name="Description"),
        slug=models.SlugField(max_length=120, unique=True, verbose_name="URL Slug"),
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['translations__name']
    
    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f"Category {self.pk}"
    
    def get_absolute_url(self):
        slug = self.safe_translation_getter('slug', any_language=True)
        if slug:
            return reverse('blog:category', kwargs={'slug': slug})
        return '#'
    
    def save(self, *args, **kwargs):
        logger.info(f"📁 Сохраняем категорию ID={self.pk}")
        
        # Сначала сохраняем объект
        super().save(*args, **kwargs)
        logger.info(f"✅ Категория сохранена, ID={self.pk}")
        
        # Потом работаем с переводимыми полями
        if hasattr(self, 'name') and self.name and not self.safe_translation_getter('slug'):
            self.slug = slugify(self.name)
            logger.info(f"🔗 Сгенерирован slug для категории: {self.slug}")
            super().save(*args, **kwargs)


class BlogPost(TranslatableModel):
    """Модель статьи блога с SEO и переводами"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
    ]
    
    # Основные поля (не переводятся)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured_image = ThumbnailerImageField(
        upload_to='blog/featured/', 
        blank=True, null=True,
        help_text="Recommended size: 1200x630px for social media"
    )
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    
    # Настройки
    is_featured = models.BooleanField(default=False, verbose_name="Featured Post")
    allow_comments = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=5, help_text="Reading time in minutes")
    
    # Теги
    tags = TaggableManager(blank=True)
    
    # Переводимые поля
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name="Title"),
        slug=models.SlugField(max_length=250, unique=True, verbose_name="URL Slug"),
        excerpt=models.TextField(
            max_length=300, 
            blank=True,
            help_text="Short description for previews and social media"
        ),
        content=RichTextUploadingField(verbose_name="Content"),
        
        # SEO поля
        meta_title=models.CharField(
            max_length=60, 
            blank=True,
            help_text="SEO title (max 60 chars). Leave blank to use post title."
        ),
        meta_description=models.CharField(
            max_length=160, 
            blank=True,
            help_text="Meta description for search engines (max 160 chars)"
        ),
        meta_keywords=models.CharField(
            max_length=255, 
            blank=True,
            help_text="SEO keywords, separated by commas"
        ),
        
        # Open Graph
        og_title=models.CharField(
            max_length=95, 
            blank=True,
            help_text="Open Graph title for social media (max 95 chars)"
        ),
        og_description=models.CharField(
            max_length=200, 
            blank=True,
            help_text="Open Graph description for social media (max 200 chars)"
        ),
        
        # Schema.org structured data
        schema_article_type=models.CharField(
            max_length=50,
            default='Article',
            choices=[
                ('Article', 'Article'),
                ('BlogPosting', 'Blog Posting'),
                ('NewsArticle', 'News Article'),
                ('TravelGuide', 'Travel Guide'),
            ],
            help_text="Schema.org article type"
        ),
    )
    
    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at', 'status']),
            models.Index(fields=['status', 'is_featured']),
        ]
    
    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or f"Post {self.pk}"
    
    def get_absolute_url(self):
        """Получаем URL статьи с правильной работой переводов"""
        slug = self.safe_translation_getter('slug', any_language=True)
        if slug:
            return reverse('blog:post_detail', kwargs={'slug': slug})
        return '#'
    
    def save(self, *args, **kwargs):
        logger.info(f"📝 ===== Начинаем сохранение поста ID={self.pk} =====")
        
        # Проверяем изображение ДО сохранения
        if self.featured_image:
            logger.info(f"🖼️ Изображение в поле featured_image: {self.featured_image.name}")
            
            # Проверяем тип объекта
            logger.info(f"🖼️ Тип объекта изображения: {type(self.featured_image)}")
            
            # Проверяем размер
            try:
                size = self.featured_image.size
                logger.info(f"📏 Размер изображения: {size} bytes")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось получить размер изображения: {e}")
            
            # Проверяем путь к файлу
            if hasattr(self.featured_image, 'path'):
                try:
                    image_path = self.featured_image.path
                    logger.info(f"📁 Путь к файлу: {image_path}")
                    
                    if os.path.exists(image_path):
                        file_size = os.path.getsize(image_path)
                        logger.info(f"✅ Файл существует до сохранения, размер: {file_size} bytes")
                        
                        # Проверяем права доступа
                        logger.info(f"🔒 Права на файл: {oct(os.stat(image_path).st_mode)[-3:]}")
                        logger.info(f"🔒 Доступен для чтения: {os.access(image_path, os.R_OK)}")
                    else:
                        logger.warning(f"⚠️ Файл НЕ существует до сохранения: {image_path}")
                        
                        # Проверяем директорию
                        dir_path = os.path.dirname(image_path)
                        logger.info(f"📁 Проверяем директорию: {dir_path}")
                        logger.info(f"📁 Директория существует: {os.path.exists(dir_path)}")
                        if os.path.exists(dir_path):
                            logger.info(f"📁 Права на директорию: {oct(os.stat(dir_path).st_mode)[-3:]}")
                            logger.info(f"📁 Доступна для записи: {os.access(dir_path, os.W_OK)}")
                        else:
                            logger.error(f"❌ Директория НЕ существует: {dir_path}")
                            
                except Exception as e:
                    logger.error(f"❌ Ошибка при проверке пути файла: {e}")
                    logger.error(f"📋 Traceback: {traceback.format_exc()}")
            else:
                logger.info(f"📁 У объекта изображения нет атрибута 'path'")
                
        else:
            logger.info("❌ Нет изображения в поле featured_image")
        
        # Проверяем основные настройки Django
        from django.conf import settings
        logger.info(f"⚙️ MEDIA_ROOT: {settings.MEDIA_ROOT}")
        logger.info(f"⚙️ MEDIA_URL: {settings.MEDIA_URL}")
        logger.info(f"⚙️ DEBUG: {settings.DEBUG}")
        
        # Сначала сохраняем объект, чтобы получить pk
        is_new = self.pk is None
        logger.info(f"🆕 Новый объект: {is_new}")
        
        try:
            logger.info("💾 Вызываем super().save()...")
            super().save(*args, **kwargs)
            logger.info(f"✅ Объект сохранен успешно, ID={self.pk}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения объекта: {e}")
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            raise
        
        # Проверяем изображение ПОСЛЕ сохранения
        if self.featured_image:
            logger.info(f"🖼️ После сохранения - проверяем изображение...")
            logger.info(f"🖼️ Имя файла: {self.featured_image.name}")
            logger.info(f"🖼️ URL: {self.featured_image.url}")
            
            if hasattr(self.featured_image, 'path'):
                try:
                    full_path = self.featured_image.path
                    logger.info(f"🖼️ Полный путь: {full_path}")
                    
                    if os.path.exists(full_path):
                        file_size = os.path.getsize(full_path)
                        logger.info(f"✅ Файл существует после сохранения")
                        logger.info(f"📏 Размер файла на диске: {file_size} bytes")
                        
                        # Проверяем права доступа
                        logger.info(f"🔒 Права на файл: {oct(os.stat(full_path).st_mode)[-3:]}")
                        logger.info(f"🔒 Доступен для чтения: {os.access(full_path, os.R_OK)}")
                        
                        # Проверяем, это ли действительно изображение
                        try:
                            with Image.open(full_path) as img:
                                logger.info(f"🖼️ Размеры изображения: {img.width}x{img.height}")
                                logger.info(f"🖼️ Режим изображения: {img.mode}")
                                logger.info(f"🖼️ Формат изображения: {img.format}")
                        except Exception as img_e:
                            logger.error(f"❌ Ошибка при открытии как изображения: {img_e}")
                            
                    else:
                        logger.error(f"❌ ФАЙЛ НЕ СУЩЕСТВУЕТ после сохранения: {full_path}")
                        
                        # Детальная проверка директории
                        dir_path = os.path.dirname(full_path)
                        logger.info(f"📁 Директория: {dir_path}")
                        logger.info(f"📁 Директория существует: {os.path.exists(dir_path)}")
                        
                        if os.path.exists(dir_path):
                            logger.info(f"📁 Содержимое директории: {os.listdir(dir_path)}")
                            logger.info(f"📁 Права на директорию: {oct(os.stat(dir_path).st_mode)[-3:]}")
                            logger.info(f"📁 Доступна для записи: {os.access(dir_path, os.W_OK)}")
                        else:
                            logger.error(f"❌ Директория НЕ существует: {dir_path}")
                            
                            # Попробуем создать директорию
                            try:
                                os.makedirs(dir_path, mode=0o755, exist_ok=True)
                                logger.info(f"✅ Директория создана: {dir_path}")
                            except Exception as dir_e:
                                logger.error(f"❌ Не удалось создать директорию: {dir_e}")
                        
                        # Проверим родительские директории
                        parent_paths = []
                        current_path = dir_path
                        while current_path != os.path.dirname(current_path):
                            parent_paths.append(current_path)
                            current_path = os.path.dirname(current_path)
                        
                        logger.info(f"🔍 Проверяем родительские директории:")
                        for path in reversed(parent_paths):
                            exists = os.path.exists(path)
                            writable = os.access(path, os.W_OK) if exists else "N/A"
                            logger.info(f"   {path}: exists={exists}, writable={writable}")
                            
                except Exception as path_e:
                    logger.error(f"❌ Ошибка при работе с путем файла: {path_e}")
                    logger.error(f"📋 Traceback: {traceback.format_exc()}")
            else:
                logger.warning(f"⚠️ У объекта изображения нет атрибута 'path' после сохранения")
        else:
            logger.warning(f"⚠️ После сохранения featured_image стало None")
        
        # Работаем с переводимыми полями
        logger.info(f"📝 Обрабатываем переводимые поля...")
        current_title = self.safe_translation_getter('title', any_language=True)
        current_slug = self.safe_translation_getter('slug', any_language=True)
        current_meta_title = self.safe_translation_getter('meta_title', any_language=True)
        current_meta_description = self.safe_translation_getter('meta_description', any_language=True)
        current_excerpt = self.safe_translation_getter('excerpt', any_language=True)
        current_content = self.safe_translation_getter('content', any_language=True)
        
        logger.info(f"📝 Title: '{current_title}'")
        logger.info(f"🔗 Slug: '{current_slug}'")
        
        need_save = False
        
        # Автогенерация slug если не указан
        if current_title and not current_slug:
            new_slug = slugify(current_title)
            self.slug = new_slug
            need_save = True
            logger.info(f"🔗 Сгенерирован slug: '{new_slug}'")
        
        # Автогенерация meta_title если не указан
        if current_title and not current_meta_title:
            new_meta_title = current_title[:60]
            self.meta_title = new_meta_title
            need_save = True
            logger.info(f"📄 Сгенерирован meta_title: '{new_meta_title}'")
        
        # Автогенерация meta_description из excerpt или content
        if not current_meta_description:
            if current_excerpt:
                new_meta_desc = current_excerpt[:160]
                self.meta_description = new_meta_desc
                need_save = True
                logger.info(f"📄 Meta description из excerpt: '{new_meta_desc}'")
            elif current_content:
                # Убираем HTML теги и берем первые 160 символов
                clean_content = re.sub(r'<[^>]+>', '', current_content)
                if clean_content:
                    new_meta_desc = clean_content[:160] + '...' if len(clean_content) > 160 else clean_content
                    self.meta_description = new_meta_desc
                    need_save = True
                    logger.info(f"📄 Meta description из content: '{new_meta_desc}'")
        
        # Сохраняем если были изменения
        if need_save:
            logger.info("🔄 Повторное сохранение для обновления переводимых полей")
            try:
                super().save(*args, **kwargs)
                logger.info("✅ Переводимые поля обновлены")
            except Exception as e:
                logger.error(f"❌ Ошибка повторного сохранения: {e}")
        
        # Оптимизация изображения
        if self.featured_image:
            logger.info("🖼️ Начинаем оптимизацию изображения")
            try:
                self.optimize_featured_image()
                logger.info("✅ Оптимизация изображения завершена")
            except Exception as e:
                logger.error(f"❌ Ошибка оптимизации изображения: {e}")
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
        
        logger.info(f"✅ ===== Сохранение поста завершено, ID={self.pk} =====")
    
    def optimize_featured_image(self):
        """Оптимизация featured image с подробным логированием и исправлением формата"""
        logger.info(f"🔧 Начинаем оптимизацию изображения для поста ID={self.pk}")
        
        if not self.featured_image:
            logger.info("❌ Нет изображения для оптимизации")
            return
            
        try:
            image_path = self.featured_image.path
            logger.info(f"🔧 Путь к изображению: {image_path}")
            logger.info(f"🔧 Имя файла: {self.featured_image.name}")
        except Exception as e:
            logger.error(f"❌ Не удалось получить путь к изображению: {e}")
            return
        
        if not os.path.exists(image_path):
            logger.error(f"❌ Файл не существует для оптимизации: {image_path}")
            return
            
        try:
            # Получаем информацию о файле до оптимизации
            original_size = os.path.getsize(image_path)
            logger.info(f"📏 Оригинальный размер файла: {original_size} bytes")
            
            # Проверяем, читается ли файл как изображение
            try:
                with Image.open(image_path) as img:
                    logger.info(f"🖼️ Размеры изображения: {img.width}x{img.height}")
                    logger.info(f"🖼️ Режим изображения: {img.mode}")
                    logger.info(f"🖼️ Формат изображения: {img.format}")
                    
                    # Создаем копию изображения в памяти
                    img_copy = img.copy()
                    
            except Exception as img_error:
                logger.error(f"❌ Не удалось открыть изображение: {img_error}")
                
                # Попробуем прочитать первые байты файла для диагностики
                try:
                    with open(image_path, 'rb') as f:
                        first_bytes = f.read(10)
                        logger.info(f"🔍 Первые 10 байт файла: {first_bytes}")
                        
                        # Проверяем магические байты
                        if first_bytes.startswith(b'\xff\xd8\xff'):
                            logger.info("🔍 Файл начинается как JPEG")
                        elif first_bytes.startswith(b'\x89PNG'):
                            logger.info("🔍 Файл начинается как PNG")
                        elif first_bytes.startswith(b'GIF'):
                            logger.info("🔍 Файл начинается как GIF")
                        else:
                            logger.warning(f"🔍 Неизвестный формат файла: {first_bytes}")
                except Exception as read_error:
                    logger.error(f"❌ Не удалось прочитать файл: {read_error}")
                
                return
            
            # Обрабатываем изображение
            processed_img = img_copy
            
            # Конвертируем в RGB если необходимо
            if processed_img.mode in ('RGBA', 'P', 'LA'):
                logger.info(f"🔄 Конвертируем из {processed_img.mode} в RGB")
                # Создаем белый фон для прозрачных изображений
                if processed_img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', processed_img.size, (255, 255, 255))
                    background.paste(processed_img, mask=processed_img.split()[-1] if processed_img.mode == 'RGBA' else None)
                    processed_img = background
                else:
                    processed_img = processed_img.convert('RGB')
            
            # Изменяем размер если больше 1200px по ширине
            if processed_img.width > 1200:
                ratio = 1200 / processed_img.width
                new_height = int(processed_img.height * ratio)
                logger.info(f"📐 Изменяем размер с {processed_img.width}x{processed_img.height} до 1200x{new_height}")
                processed_img = processed_img.resize((1200, new_height), Image.Resampling.LANCZOS)
            else:
                logger.info(f"📐 Размер изображения оптимальный: {processed_img.width}x{processed_img.height}")
            
            # Создаем временный файл для проверки
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Сохраняем оптимизированное изображение во временный файл
                logger.info(f"💾 Сохраняем во временный файл: {temp_path}")
                processed_img.save(temp_path, 'JPEG', quality=85, optimize=True)
                
                # Проверяем временный файл
                if os.path.exists(temp_path):
                    temp_size = os.path.getsize(temp_path)
                    logger.info(f"✅ Временный файл создан, размер: {temp_size} bytes")
                    
                    # Перезаписываем оригинальный файл
                    import shutil
                    shutil.move(temp_path, image_path)
                    logger.info(f"🔄 Заменили оригинальный файл")
                    
                    # Проверяем результат
                    if os.path.exists(image_path):
                        new_size = os.path.getsize(image_path)
                        savings = original_size - new_size
                        savings_percent = (savings / original_size * 100) if original_size > 0 else 0
                        
                        logger.info(f"📏 Новый размер файла: {new_size} bytes")
                        logger.info(f"💾 Изменение размера: {savings} bytes ({savings_percent:.1f}%)")
                        
                        # Проверяем, что новый файл можно открыть
                        try:
                            with Image.open(image_path) as test_img:
                                logger.info(f"✅ Оптимизированный файл корректен: {test_img.width}x{test_img.height}")
                        except Exception as test_error:
                            logger.error(f"❌ Оптимизированный файл поврежден: {test_error}")
                    else:
                        logger.error(f"❌ Файл исчез после замены!")
                else:
                    logger.error(f"❌ Временный файл не создался!")
                    
                # Удаляем временный файл если он остался
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"❌ Ошибка оптимизации изображения: {e}")
            logger.error(f"📋 Полный traceback: {traceback.format_exc()}")
            
            # Попробуем проанализировать ошибку
            if "cannot identify image file" in str(e):
                logger.error("💡 Возможно, файл поврежден или не является изображением")
                logger.error("💡 Попробуйте загрузить изображение в формате PNG или JPG")
            elif "Permission denied" in str(e):
                logger.error("💡 Проблемы с правами доступа к файлу")
            elif "No such file or directory" in str(e):
                logger.error("💡 Файл не найден во время оптимизации")
    
    def get_next_post(self):
        """Следующая статья"""
        return BlogPost.objects.filter(
            published_at__gt=self.published_at,
            status='published'
        ).order_by('published_at').first()
    
    def get_previous_post(self):
        """Предыдущая статья"""
        return BlogPost.objects.filter(
            published_at__lt=self.published_at,
            status='published'
        ).order_by('-published_at').first()
    
    def increment_views(self):
        """Увеличить счетчик просмотров"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_related_posts(self, limit=3):
        """Похожие статьи"""
        return BlogPost.objects.filter(
            category=self.category,
            status='published'
        ).exclude(pk=self.pk).order_by('-published_at')[:limit]
    
    def get_display_title(self):
        """Получить заголовок для отображения"""
        return self.safe_translation_getter('title', any_language=True) or f"Post {self.pk}"
    
    def get_display_content(self):
        """Получить контент для отображения"""
        return self.safe_translation_getter('content', any_language=True) or ''
    
    def get_display_excerpt(self):
        """Получить описание для отображения"""
        excerpt = self.safe_translation_getter('excerpt', any_language=True)
        if excerpt:
            return excerpt
        
        # Если нет excerpt, создаем из content
        content = self.get_display_content()
        if content:
            clean_content = re.sub(r'<[^>]+>', '', content)
            return clean_content[:300] + '...' if len(clean_content) > 300 else clean_content
        
        return ''
    
    def get_display_meta_title(self):
        """Получить meta title для отображения"""
        return (self.safe_translation_getter('meta_title', any_language=True) or 
                self.get_display_title())
    
    def get_display_meta_description(self):
        """Получить meta description для отображения"""
        return (self.safe_translation_getter('meta_description', any_language=True) or 
                self.get_display_excerpt())
    
    def generate_schema_json(self):
        """Генерация JSON-LD разметки"""
        from django.conf import settings
        
        schema = {
            "@context": "https://schema.org",
            "@type": self.safe_translation_getter('schema_article_type', any_language=True) or 'Article',
            "headline": self.get_display_meta_title(),
            "description": self.get_display_meta_description(),
            "author": {
                "@type": "Person",
                "name": self.author.get_full_name() or self.author.username
            },
            "publisher": {
                "@type": "Organization",
                "name": "Abroads Tours",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/static/img/logo.png"
                }
            },
            "datePublished": self.published_at.isoformat(),
            "dateModified": self.updated_at.isoformat(),
            "url": f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}{self.get_absolute_url()}",
        }
        
        if self.featured_image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}{self.featured_image.url}",
                "width": 1200,
                "height": 630
            }
        
        if self.category:
            schema["articleSection"] = str(self.category)
        
        if self.tags.exists():
            schema["keywords"] = [tag.name for tag in self.tags.all()]
        
        return schema


class BlogImage(models.Model):
    """Модель для изображений в статьях"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='images')
    image = ThumbnailerImageField(upload_to='blog/images/')
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Blog Image"
        verbose_name_plural = "Blog Images"
    
    def __str__(self):
        post_title = self.post.safe_translation_getter('title', any_language=True) or f"Post {self.post.pk}"
        return f"Image for {post_title}"
    
    def save(self, *args, **kwargs):
        logger.info(f"🖼️ Сохраняем BlogImage для поста {self.post.pk if self.post else 'None'}")
        
        if self.image:
            logger.info(f"🖼️ Изображение: {self.image.name}")
        
        super().save(*args, **kwargs)
        logger.info(f"✅ BlogImage сохранен, ID={self.pk}")


class BlogComment(models.Model):
    """Комментарии к статьям"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-created_at']
    
    def __str__(self):
        post_title = self.post.safe_translation_getter('title', any_language=True) or f"Post {self.post.pk}"
        return f"Comment by {self.name} on {post_title}"
    
    def save(self, *args, **kwargs):
        logger.info(f"💬 Сохраняем комментарий от {self.name} к посту {self.post.pk if self.post else 'None'}")
        super().save(*args, **kwargs)
        logger.info(f"✅ Комментарий сохранен, ID={self.pk}")
