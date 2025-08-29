# backend/tours/views.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import logging

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from django.views.generic import DetailView, ListView

from .models import Tour, TourCategory, TourDifficulty

# Настройка логгера
logger = logging.getLogger("tours")


class TourListView(ListView):
    """Простой список всех туров"""

    model = Tour
    template_name = "tours/tour_list.html"
    context_object_name = "tours"
    paginate_by = 12

    def get_queryset(self):
        """Возвращаем только опубликованные туры"""
        logger.info("📋 Получаем список туров")

        queryset = (
            Tour.objects.filter(status="published")
            .select_related("author", "category", "difficulty")
            .prefetch_related("tags", "images")
            .order_by("-is_featured", "sort_order", "-created_at")
        )

        total_tours = queryset.count()
        logger.info(f"📋 Найдено туров: {total_tours}")

        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем контекст для страницы списка туров"""
        logger.info("🔧 Формируем контекст для списка туров")

        context = super().get_context_data(**kwargs)
        tours = context.get("tours", [])

        logger.info(f"📋 Отображаем {len(tours)} туров на странице")

        # Категории для навигации
        context["categories"] = TourCategory.objects.filter(is_active=True).order_by(
            "sort_order"
        )

        # SEO
        context["page_title"] = "All Tours - Abroads Tours"
        context["page_description"] = (
            "Discover our amazing tours. Small group experiences from Milan to Lake Como, wine regions, and more."
        )

        logger.info("✅ Контекст для списка туров сформирован")
        return context


class TourCategoryView(ListView):
    """Туры определенной категории"""

    model = Tour
    template_name = "tours/category.html"
    context_object_name = "tours"
    paginate_by = 12

    def get_queryset(self):
        """Получаем туры категории"""
        category_slug = self.kwargs["slug"]
        logger.info(f"📂 Получаем туры для категории: '{category_slug}'")

        self.category = get_object_or_404(
            TourCategory, translations__slug=category_slug, is_active=True
        )

        category_name = self.category.safe_translation_getter("name", any_language=True)
        logger.info(f"📂 Категория найдена: '{category_name}' (ID={self.category.id})")

        queryset = (
            Tour.objects.filter(category=self.category, status="published")
            .select_related("author", "category", "difficulty")
            .prefetch_related("tags", "images")
            .order_by("-is_featured", "sort_order", "-created_at")
        )

        total_tours = queryset.count()
        logger.info(f"📋 Туров в категории: {total_tours}")

        return queryset

    def get_context_data(self, **kwargs):
        """Формируем контекст для категории"""
        logger.info("🔧 Формируем контекст для категории туров")

        context = super().get_context_data(**kwargs)
        context["category"] = self.category

        category_name = self.category.safe_translation_getter("name", any_language=True)
        category_description = self.category.safe_translation_getter(
            "description", any_language=True
        )

        # SEO
        context["page_title"] = f"{category_name} - Tours"
        context["page_description"] = (
            category_description
            or f"Discover amazing {category_name.lower()} with Abroads Tours"
        )

        logger.info(f"📂 Контекст категории: {category_name}")
        return context


class TourDetailView(DetailView):
    """Детальная страница тура"""

    model = Tour
    template_name = "tours/tour_detail.html"
    context_object_name = "tour"
    slug_field = "translations__slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Возвращаем только опубликованные туры"""
        logger.info("📄 Получаем queryset для детальной страницы тура")

        queryset = (
            Tour.objects.filter(status="published")
            .select_related("author", "category", "difficulty")
            .prefetch_related(
                "tags",
                "images",
                "faqs",
                "reviews", 
                "meeting_points",  # ИСПРАВЛЕНО: используем meeting_points
            )
        )

        return queryset

    def get_object(self, queryset=None):
        """Получаем объект тура"""
        logger.info("🔍 Поиск тура по slug")

        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg)
        logger.info(f"🔍 Ищем тур с slug: '{slug}'")

        if slug is None:
            logger.error("❌ Slug не предоставлен")
            raise Http404("No slug provided")

        try:
            # Ищем тур по slug в переводах
            obj = queryset.get(translations__slug=slug)
            logger.info(
                f"✅ Тур найден: ID={obj.id}, Title='{obj.safe_translation_getter('title', any_language=True)}'"
            )

            # Увеличиваем счетчик просмотров
            logger.info("👁️ Увеличиваем счетчик просмотров")
            obj.increment_views()

            return obj

        except Tour.DoesNotExist:
            logger.error(f"❌ Тур с slug '{slug}' не найден")
            raise Http404("Tour not found")
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске тура: {e}")
            raise

    def get_context_data(self, **kwargs):
        """Формируем контекст для детальной страницы"""
        logger.info("🔧 Формируем контекст для детальной страницы тура")

        context = super().get_context_data(**kwargs)
        tour = self.get_object()

        # SEO
        context["page_title"] = tour.safe_translation_getter(
            "meta_title", any_language=True
        ) or tour.safe_translation_getter("title", any_language=True)
        context["page_description"] = tour.safe_translation_getter(
            "meta_description", any_language=True
        ) or tour.safe_translation_getter("short_description", any_language=True)

        # Похожие туры
        logger.info("🔗 Получаем похожие туры")
        related_tours = tour.get_related_tours(limit=4)
        context["related_tours"] = related_tours
        logger.info(f"🔗 Найдено похожих туров: {len(related_tours)}")

        # Изображения для галереи (первые 4 для основной сетки)
        context["gallery_images"] = tour.images.filter(is_featured=True).order_by(
            "sort_order"
        )[:4]
        context["all_images"] = tour.images.all().order_by("sort_order")

        # FAQ (активные)
        context["faqs"] = tour.faqs.filter(is_active=True).order_by("sort_order")

        # Отзывы (проверенные)
        context["reviews"] = tour.reviews.filter(is_verified=True).order_by(
            "-is_featured", "sort_order", "-review_date"
        )

        # Точки встречи - ИСПРАВЛЕНО: используем meeting_points
        context["meeting_points"] = tour.meeting_points.all().order_by(
            "sort_order"
        )

        # Код бронирования
        try:
            context["booking_code"] = tour.booking_code
        except:
            context["booking_code"] = None

        logger.info("✅ Контекст для детальной страницы тура сформирован")
        return context


def get_similar_tours(request, tour_id):
    """AJAX для получения похожих туров"""
    try:
        tour = get_object_or_404(Tour, id=tour_id, status="published")
        similar_tours = tour.get_related_tours(limit=4)

        data = []
        for similar_tour in similar_tours:
            data.append(
                {
                    "id": similar_tour.id,
                    "title": similar_tour.safe_translation_getter(
                        "title", any_language=True
                    ),
                    "short_description": similar_tour.safe_translation_getter(
                        "short_description", any_language=True
                    ),
                    "price": float(similar_tour.price_adult),
                    "duration": similar_tour.get_duration_display(),
                    "rating": float(similar_tour.rating),
                    "featured_image": (
                        similar_tour.featured_image.url
                        if similar_tour.featured_image
                        else None
                    ),
                    "url": similar_tour.get_absolute_url(),
                    "location": similar_tour.location or (
                        similar_tour.category.safe_translation_getter(
                            "name", any_language=True
                        )
                        if similar_tour.category
                        else None
                    ),
                }
            )

        return JsonResponse({"tours": data})

    except Exception as e:
        logger.error(f"❌ Ошибка получения похожих туров: {e}")
        return JsonResponse({"error": "Error loading similar tours"}, status=500)
