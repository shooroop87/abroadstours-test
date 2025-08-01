# flake8: noqa
from core.services.multi_reviews_service import MultiSourceReviewsService
from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Debug exactly where reviews are coming from and show their sources"

    def handle(self, *args, **options):
        self.stdout.write("🔍 ОТЛАДКА ИСТОЧНИКОВ ОТЗЫВОВ")
        self.stdout.write("=" * 50)

        # Проверяем что в кэше
        self.check_cached_reviews()

        # Тестируем каждый источник отдельно
        self.test_individual_sources()

        # Проверяем текущую страницу
        self.check_current_page_reviews()

    def check_cached_reviews(self):
        """Проверяем закэшированные отзывы"""
        self.stdout.write("\n💾 ЗАКЭШИРОВАННЫЕ ОТЗЫВЫ:")
        self.stdout.write("-" * 30)

        cache_key = "multi_reviews_page_1_7"
        cached_data = cache.get(cache_key)

        if cached_data:
            reviews = cached_data.get("reviews", [])
            self.stdout.write(f"📊 Найдено в кэше: {len(reviews)} отзывов")

            for i, review in enumerate(reviews, 1):
                author = review.get("author_name", "Unknown")
                source = review.get("source", "unknown")
                text_preview = review.get("text", "")[:50] + "..."
                date = review.get("relative_time_description", "No date")
                review_id = review.get("review_id", "No ID")

                source_icon = (
                    "🟢"
                    if source == "tripadvisor"
                    else "🔵" if source == "google" else "⚪"
                )

                self.stdout.write(f"\n{i}. {source_icon} {source.upper()}")
                self.stdout.write(f"   👤 Автор: {author}")
                self.stdout.write(f"   📅 Дата: {date}")
                self.stdout.write(f"   🆔 ID: {review_id}")
                self.stdout.write(f"   💬 Текст: {text_preview}")
        else:
            self.stdout.write("❌ Нет закэшированных отзывов")

    def test_individual_sources(self):
        """Тестируем каждый источник отдельно"""
        self.stdout.write("\n🧪 ТЕСТИРОВАНИЕ ИСТОЧНИКОВ:")
        self.stdout.write("-" * 30)

        service = MultiSourceReviewsService()

        # Тест TripAdvisor
        self.stdout.write("\n🟢 TripAdvisor API:")
        try:
            ta_reviews = service._fetch_tripadvisor_reviews()
            if ta_reviews:
                self.stdout.write(f"   ✅ Получено: {len(ta_reviews)} отзывов")
                for i, review in enumerate(ta_reviews[:3], 1):
                    author = review.get("author_name", "Unknown")
                    date = review.get("relative_time_description", "No date")
                    self.stdout.write(f"   {i}. {author} - {date}")
            else:
                self.stdout.write("   ❌ Отзывы не получены")
        except Exception as e:
            self.stdout.write(f"   💥 Ошибка: {str(e)}")

        # Тест Google
        self.stdout.write("\n🔵 Google Places API:")
        try:
            google_reviews = service._fetch_google_reviews()
            if google_reviews:
                self.stdout.write(f"   ✅ Получено: {len(google_reviews)} отзывов")
                for i, review in enumerate(google_reviews[:3], 1):
                    author = review.get("author_name", "Unknown")
                    date = review.get("relative_time_description", "No date")
                    self.stdout.write(f"   {i}. {author} - {date}")
            else:
                self.stdout.write("   ❌ Отзывы не получены")
        except Exception as e:
            self.stdout.write(f"   💥 Ошибка: {str(e)}")

    def check_current_page_reviews(self):
        """Проверяем отзывы текущей страницы"""
        self.stdout.write("\n📄 ТЕКУЩАЯ СТРАНИЦА:")
        self.stdout.write("-" * 30)

        service = MultiSourceReviewsService()

        # Очищаем кэш и получаем свежие данные
        service.clear_cache()
        current_data = service.get_reviews(page=1, per_page=7)

        if current_data and current_data.get("reviews"):
            reviews = current_data["reviews"]
            sources_used = current_data.get("sources_used", {})

            self.stdout.write(f"📊 Всего отзывов: {len(reviews)}")
            self.stdout.write(f"🔧 Источники: {sources_used}")

            # Группируем по источникам
            by_source = {}
            for review in reviews:
                source = review.get("source", "unknown")
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(review)

            for source, source_reviews in by_source.items():
                source_icon = (
                    "🟢"
                    if source == "tripadvisor"
                    else "🔵" if source == "google" else "⚪"
                )
                self.stdout.write(
                    f"\n{source_icon} {source.upper()}: {len(source_reviews)} отзывов"
                )

                for review in source_reviews:
                    author = review.get("author_name", "Unknown")
                    date = review.get("relative_time_description", "No date")
                    text = review.get("text", "")[:80] + "..."
                    self.stdout.write(f"   • {author} ({date}): {text}")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("💡 РЕКОМЕНДАЦИИ:")
        self.stdout.write("1. Проверьте Place ID для Google Places API")
        self.stdout.write(
            "2. Убедитесь что TripAdvisor API ключ привязан к правильному бизнесу"
        )
        self.stdout.write(
            "3. Сравните авторов отзывов с вашими страницами Google/TripAdvisor"
        )
        self.stdout.write("4. Возможно API возвращает отзывы с других локаций")
