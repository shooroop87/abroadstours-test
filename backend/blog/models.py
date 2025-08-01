# backend/blog/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from parler.models import TranslatableModel, TranslatedFields
from taggit.managers import TaggableManager
from PIL import Image
import os


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
        return reverse('blog:category', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
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
    featured_image = models.ImageField(
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
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        # Автогенерация slug если не указан
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        
        # Автогенерация meta_title если не указан
        if not self.meta_title and self.title:
            self.meta_title = self.title[:60]
        
        # Автогенерация meta_description из excerpt или content
        if not self.meta_description:
            if self.excerpt:
                self.meta_description = self.excerpt[:160]
            elif self.content:
                # Убираем HTML теги и берем первые 160 символов
                import re
                clean_content = re.sub(r'<[^>]+>', '', self.content)
                self.meta_description = clean_content[:160] + '...' if len(clean_content) > 160 else clean_content
        
        super().save(*args, **kwargs)
        
        # Оптимизация изображения
        if self.featured_image:
            self.optimize_featured_image()
    
    def optimize_featured_image(self):
        """Оптимизация featured image"""
        if not self.featured_image:
            return
            
        image_path = self.featured_image.path
        if os.path.exists(image_path):
            with Image.open(image_path) as img:
                # Конвертируем в RGB если необходимо
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Изменяем размер если больше 1200px по ширине
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
                
                # Сохраняем с оптимизацией
                img.save(image_path, 'JPEG', quality=85, optimize=True)
    
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
    
    def generate_schema_json(self):
        """Генерация JSON-LD разметки"""
        from django.conf import settings
        
        schema = {
            "@context": "https://schema.org",
            "@type": self.schema_article_type,
            "headline": self.meta_title or self.title,
            "description": self.meta_description,
            "author": {
                "@type": "Person",
                "name": self.author.get_full_name() or self.author.username
            },
            "publisher": {
                "@type": "Organization",
                "name": "Abroads Tours",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{settings.SITE_URL}/static/img/logo.png"
                }
            },
            "datePublished": self.published_at.isoformat(),
            "dateModified": self.updated_at.isoformat(),
            "url": f"{settings.SITE_URL}{self.get_absolute_url()}",
        }
        
        if self.featured_image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": f"{settings.SITE_URL}{self.featured_image.url}",
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
    image = models.ImageField(upload_to='blog/images/')
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Blog Image"
        verbose_name_plural = "Blog Images"
    
    def __str__(self):
        return f"Image for {self.post.title}"


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
        return f"Comment by {self.name} on {self.post.title}"
