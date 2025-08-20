# backend/tours/models.py - ИСПРАВЛЕННАЯ ВЕРСИЯ БЕЗ КОНФЛИКТОВ
import logging
import os
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from parler.models import TranslatableModel, TranslatedFields
from taggit.managers import TaggableManager

logger = logging.getLogger('tours.models')

class TourCategory(TranslatableModel):
    """Категории туров (Wine Tours, Lake Como Tours, etc.)"""
    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name="Category Name"),
        slug=models.SlugField(max_length=120, unique=True, verbose_name="URL Slug"),
        description=models.TextField(blank=True, verbose_name="Description"),
    )
    
    icon = models.CharField(
        max_length=50, 
        default='icon-mountain',
        help_text="CSS class for category icon (e.g., icon-wine, icon-mountain)"
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tour Category"
        verbose_name_plural = "Tour Categories"
        ordering = ['sort_order', 'translations__name']
    
    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f"Category {self.pk}"
    
    def get_absolute_url(self):
        slug = self.safe_translation_getter('slug', any_language=True)
        if slug:
            return reverse('tour_category', kwargs={'slug': slug})
        return '#'


class TourDifficulty(models.Model):
    """Уровень сложности тура"""
    name = models.CharField(max_length=50, unique=True)
    level = models.IntegerField(help_text="1=Easy, 2=Moderate, 3=Challenging, 4=Difficult, 5=Expert")
    icon = models.CharField(max_length=50, default='icon-difficulty')
    color = models.CharField(max_length=7, default='#46b450', help_text="Hex color code")
    
    class Meta:
        verbose_name = "Difficulty Level"
        verbose_name_plural = "Difficulty Levels"
        ordering = ['level']
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"


class Tour(TranslatableModel):
    """Основная модель тура"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    TOUR_TYPE_CHOICES = [
        ('wine_tour', 'Wine Tour'),
        ('city_tour', 'City Tour'),
        ('nature_tour', 'Nature Tour'),
        ('cultural_tour', 'Cultural Tour'),
        ('adventure_tour', 'Adventure Tour'),
        ('food_tour', 'Food Tour'),
        ('custom', 'Custom'),
    ]
    
    # Основные поля (не переводятся)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tours')
    category = models.ForeignKey(TourCategory, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.ForeignKey(TourDifficulty, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    tour_type = models.CharField(max_length=20, choices=TOUR_TYPE_CHOICES, default='custom')
    
    # ДОБАВЛЯЕМ: Географическое место тура
    location = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Geographic location (e.g., 'Alba, Piedmont, Italy')",
        verbose_name="Tour Location"
    )
    
    # Базовые характеристики тура
    duration_hours = models.IntegerField(default=8, help_text="Duration in hours")
    duration_minutes = models.IntegerField(default=0, help_text="Additional minutes (0-59)")
    max_group_size = models.IntegerField(default=19, help_text="Maximum number of participants")
    
    # Цены
    price_adult = models.DecimalField(max_digits=8, decimal_places=2, help_text="Price per adult in EUR")
    price_child = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, 
        help_text="Price per child in EUR (optional)"
    )
    price_private = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Private tour price in EUR (optional)"
    )
    
    # Опции
    free_cancellation = models.BooleanField(default=True)
    reserve_now_pay_later = models.BooleanField(default=True)
    instant_confirmation = models.BooleanField(default=True)
    
    # Языки (можно выбрать несколько)
    languages = models.CharField(
        max_length=200, 
        default='English',
        help_text="Comma-separated languages (e.g., 'English, Italian, French')"
    )
    
    # Изображения
    featured_image = models.ImageField(
        upload_to='tours/featured/', 
        help_text="Main tour image (recommended: 1200x800px)"
    )
    
    # Рейтинг и отзывы
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=5.0,
        help_text="Tour rating (0.00-5.00)"
    )
    reviews_count = models.IntegerField(default=0, help_text="Number of reviews")
    
    # Статистика
    views_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    
    # Служебные поля
    is_featured = models.BooleanField(default=False, verbose_name="Featured Tour")
    sort_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Теги
    tags = TaggableManager(blank=True)
    
    class Meta:
        verbose_name = "Tour"
        verbose_name_plural = "Tours"
        ordering = ['-is_featured', 'sort_order', '-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        title = self.safe_translation_getter('title', any_language=True)
        return title or f"Tour {self.pk}"
    
    # Переводимые поля
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name="Tour Title"),
        slug=models.SlugField(max_length=250, unique=True, verbose_name="URL Slug"),
        
        # Краткое описание
        short_description=models.CharField(
            max_length=300, 
            help_text="Brief description for tour cards and previews"
        ),
        
        # Основные разделы контента
        tour_highlights=RichTextUploadingField(
            blank=True,
            verbose_name="Tour Highlights",
            help_text="Key selling points and highlights of the tour"
        ),
        
        why_unique=RichTextUploadingField(
            blank=True,
            verbose_name="Why This Tour Is Unique",
            help_text="What makes this tour special and different"
        ),
        
        what_experience=RichTextUploadingField(
            blank=True,
            verbose_name="What You'll Experience", 
            help_text="Detailed description of the tour experience"
        ),
        
        whats_included=RichTextUploadingField(
            blank=True,
            verbose_name="What's Included",
            help_text="List of included services and features"
        ),
        
        whats_not_included=RichTextUploadingField(
            blank=True,
            verbose_name="What's Not Included",
            help_text="List of services not included in the price"
        ),
        
        # ДОБАВЛЯЕМ: Private Tour Information
        private_tour_info=RichTextUploadingField(
            blank=True,
            verbose_name="Private Tour Information",
            help_text="Information about private tour options and pricing"
        ),
        
        # SEO поля
        meta_title=models.CharField(
            max_length=60, 
            blank=True,
            help_text="SEO title (max 60 chars). Leave blank to use tour title."
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
    )
    
    # Методы модели
    def get_absolute_url(self):
        """Получаем URL тура"""
        slug = self.safe_translation_getter('slug', any_language=True)
        if not slug:
            # Если нет slug, генерируем его из title
            title = self.safe_translation_getter('title', any_language=True)
            if title:
                slug = slugify(title)
            else:
                slug = f"tour-{self.pk}"
        
        # Проверяем, есть ли статичный URL для этого тура
        static_tours_mapping = {
            'barolo-wine-tasting-tour-from-milan-alba': 'alba_barolo_tour',
            'barolo-barbaresco-wine-tasting-from-milan-visit-alba': 'barolo_barbaresco_from_milan',
            'kick-off-walking-tour-in-milano': 'kick_off_walking_tour_in_milano',
            'como-city-walking-tour-with-the-boat-cruise-small-group-tour': 'como_city_walking_tour',
            'lake-como-and-lugano-small-group-tour-from-milan': 'lake_como_and_lugano_tour',
            'bellagio-varenna-from-milan': 'bellagio_varenna_tour',
            'from-milan-lake-como-and-lugano-tour-with-morcote': 'lake_como_lugano_morcote_tour',
        }
        
        # Если есть статичный URL, используем его
        if slug in static_tours_mapping:
            return reverse(static_tours_mapping[slug])
        
        # Иначе используем динамический URL
        return reverse('tour_detail', kwargs={'slug': slug})
    
    def get_duration_display(self):
        """Форматированное отображение продолжительности"""
        if self.duration_minutes > 0:
            return f"{self.duration_hours}h {self.duration_minutes}m"
        return f"{self.duration_hours} hours"
    
    def get_price_display(self):
        """Форматированное отображение цены"""
        return f"€{self.price_adult:.0f}"
    
    def get_languages_list(self):
        """Список языков как массив"""
        return [lang.strip() for lang in self.languages.split(',') if lang.strip()]
    
    def get_rating_stars(self):
        """Количество полных звезд для рейтинга"""
        return int(self.rating)
    
    def increment_views(self):
        """Увеличить счетчик просмотров"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_bookings(self):
        """Увеличить счетчик бронирований"""
        self.booking_count += 1
        self.save(update_fields=['booking_count'])
    
    def get_related_tours(self, limit=4):
        """Похожие туры"""
        return Tour.objects.filter(
            category=self.category,
            status='published'
        ).exclude(pk=self.pk).order_by('-is_featured', 'sort_order')[:limit]
    
    def save(self, *args, **kwargs):
        """Кастомная логика сохранения"""
        logger.info(f"🎯 Сохраняем тур ID={self.pk}")
        
        # Сначала сохраняем объект
        super().save(*args, **kwargs)
        
        # Автогенерация slug если не указан
        current_title = self.safe_translation_getter('title', any_language=True)
        current_slug = self.safe_translation_getter('slug', any_language=True)
        
        if current_title and not current_slug:
            self.slug = slugify(current_title)
            super().save(*args, **kwargs)
            logger.info(f"🔗 Сгенерирован slug: {self.slug}")
        
        logger.info(f"✅ Тур сохранен, ID={self.pk}")


class TourImage(models.Model):
    """Галерея изображений для тура"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    sort_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Show in main gallery grid")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tour Image"
        verbose_name_plural = "Tour Images"
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        tour_title = self.tour.safe_translation_getter('title', any_language=True)
        return f"Image for {tour_title or f'Tour {self.tour.pk}'}"


class TourFAQ(TranslatableModel):
    """FAQ для туров"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='faqs')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    translations = TranslatedFields(
        question=models.CharField(max_length=300, verbose_name="Question"),
        answer=RichTextUploadingField(verbose_name="Answer"),
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tour FAQ"
        verbose_name_plural = "Tour FAQs"
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        question = self.safe_translation_getter('question', any_language=True)
        tour_title = self.tour.safe_translation_getter('title', any_language=True)
        return f"FAQ: {question[:50] or 'No question'} ({tour_title or f'Tour {self.tour.pk}'})"


class TourReview(TranslatableModel):
    """Отзывы о турах"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews')
    
    # Информация об авторе
    author_name = models.CharField(max_length=100)
    author_location = models.CharField(max_length=100, blank=True)
    author_avatar = models.ImageField(upload_to='tours/reviews/', blank=True)
    
    # Рейтинг
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    
    # Дата отзыва
    review_date = models.DateField()
    
    # Опции отображения
    is_featured = models.BooleanField(default=False, help_text="Show in featured reviews")
    is_verified = models.BooleanField(default=True, help_text="Verified review")
    sort_order = models.IntegerField(default=0)
    
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name="Review Title"),
        content=models.TextField(verbose_name="Review Content"),
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tour Review"
        verbose_name_plural = "Tour Reviews"
        ordering = ['-is_featured', 'sort_order', '-review_date']
    
    def __str__(self):
        title = self.safe_translation_getter('title', any_language=True)
        tour_title = self.tour.safe_translation_getter('title', any_language=True)
        return f"Review by {self.author_name}: {title or 'No title'} ({tour_title or f'Tour {self.tour.pk}'})"
    
    def get_stars_range(self):
        """Возвращает range для отображения звезд"""
        return range(self.rating)


class TourMeetingPoint(TranslatableModel):
    """Точки встречи для тура - ИСПРАВЛЕНО: используем 'meeting_points' вместо 'tour_meeting_points'"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='meeting_points')
    
    # Время встречи
    meeting_time = models.TimeField(help_text="Meeting time (e.g., 08:55)")
    
    # Координаты
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Ссылки
    google_maps_url = models.URLField(blank=True)
    
    sort_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False, help_text="Primary meeting point")
    
    translations = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name="Meeting Point Name"),
        address=models.TextField(verbose_name="Full Address"),
        description=models.TextField(
            blank=True,
            verbose_name="Additional Instructions",
            help_text="Additional directions or landmarks"
        ),
    )
    
    class Meta:
        verbose_name = "Meeting Point"
        verbose_name_plural = "Meeting Points"
        ordering = ['sort_order', 'meeting_time']
    
    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True)
        tour_title = self.tour.safe_translation_getter('title', any_language=True)
        return f"{name or 'Meeting Point'} - {tour_title or f'Tour {self.tour.pk}'} ({self.meeting_time})"


class BookingCode(models.Model):
    """HTML код для системы бронирования"""
    tour = models.OneToOneField(Tour, on_delete=models.CASCADE, related_name='booking_code')
    
    # Rezdy или другая система бронирования
    booking_system = models.CharField(
        max_length=50,
        choices=[
            ('rezdy', 'Rezdy'),
            ('custom', 'Custom HTML'),
            ('none', 'No Booking System'),
        ],
        default='rezdy'
    )
    
    # HTML код виджета бронирования
    html_code = models.TextField(
        help_text="Full HTML code for booking widget",
        blank=True
    )
    
    # Дополнительные скрипты
    additional_scripts = models.TextField(
        blank=True,
        help_text="Additional JavaScript code if needed"
    )
    
    # Настройки
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Booking Code"
        verbose_name_plural = "Booking Codes"
    
    def __str__(self):
        tour_title = self.tour.safe_translation_getter('title', any_language=True)
        return f"Booking for {tour_title or f'Tour {self.tour.pk}'} ({self.booking_system})"