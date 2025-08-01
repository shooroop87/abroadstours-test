# flake8: noqa
import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test TripAdvisor Content API v1 with correct location_id = 24938712"

    def handle(self, *args, **options):
        api_key = getattr(settings, "TRIPADVISOR_API_KEY", "")
        location_id = "24938712"  # Ваш правильный location_id

        self.stdout.write("🔍 ТЕСТИРОВАНИЕ TRIPADVISOR CONTENT API V1")
        self.stdout.write("=" * 50)
        self.stdout.write(
            f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ No API key found"
        )
        self.stdout.write(f"🆔 Location ID: {location_id}")

        if not api_key:
            self.stdout.write(self.style.ERROR("❌ TripAdvisor API key not configured"))
            return

        # Сначала получаем информацию о локации
        self.test_location_details(api_key, location_id)

        # Затем тестируем отзывы
        self.test_location_reviews(api_key, location_id)

    def test_location_details(self, api_key, location_id):
        """Тестируем получение информации о локации"""
        self.stdout.write("\n📍 ИНФОРМАЦИЯ О ЛОКАЦИИ:")
        self.stdout.write("-" * 30)

        details_url = (
            f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details"
        )
        params = {"key": api_key, "language": "en", "currency": "USD"}

        try:
            self.stdout.write(f"📡 Запрос: {details_url}")
            response = requests.get(details_url, params=params, timeout=15)

            self.stdout.write(f"📊 Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                name = data.get("name", "N/A")
                description = data.get("description", "N/A")
                location_string = data.get("location_string", "N/A")
                rating = data.get("rating", "N/A")
                num_reviews = data.get("num_reviews", "N/A")

                self.stdout.write(f"✅ Название: {name}")
                self.stdout.write(f"📍 Местоположение: {location_string}")
                self.stdout.write(f"⭐ Рейтинг: {rating}")
                self.stdout.write(f"📊 Количество отзывов: {num_reviews}")

                if description and len(description) > 10:
                    self.stdout.write(f"📝 Описание: {description[:100]}...")

                # Проверяем категории
                categories = data.get("category", {})
                if categories:
                    self.stdout.write(f"🏷️ Категория: {categories.get('name', 'N/A')}")

            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ HTTP Error: {response.status_code}")
                )
                self.stdout.write(f"Response: {response.text}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Exception: {str(e)}"))

    def test_location_reviews(self, api_key, location_id):
        """Тестируем получение отзывов для локации"""
        self.stdout.write("\n📝 ОТЗЫВЫ О ЛОКАЦИИ:")
        self.stdout.write("-" * 30)

        reviews_url = (
            f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/reviews"
        )
        params = {
            "key": api_key,
            "language": "en",
            "limit": 10,  # Получаем до 10 отзывов
        }

        try:
            self.stdout.write(f"📡 Запрос: {reviews_url}")
            self.stdout.write(f"📝 Параметры: {params}")

            response = requests.get(reviews_url, params=params, timeout=15)

            self.stdout.write(f"📊 Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                reviews = data.get("data", [])

                self.stdout.write(f"✅ Найдено отзывов: {len(reviews)}")

                if reviews:
                    self.stdout.write("\n📋 ПРИМЕРЫ ОТЗЫВОВ:")

                    for i, review in enumerate(reviews[:3], 1):  # Показываем первые 3
                        user = review.get("user", {})
                        username = user.get("username", "Anonymous")

                        rating = review.get("rating", "N/A")
                        title = review.get("title", "")
                        text = review.get("text", "")
                        published_date = review.get("published_date", "N/A")

                        self.stdout.write(f"\n{i}. 👤 Автор: {username}")
                        self.stdout.write(f"   ⭐ Рейтинг: {rating}")
                        self.stdout.write(f"   📅 Дата: {published_date}")

                        if title:
                            self.stdout.write(f"   📌 Заголовок: {title}")

                        if text:
                            preview_text = (
                                text[:150] + "..." if len(text) > 150 else text
                            )
                            self.stdout.write(f"   💬 Текст: {preview_text}")

                        # Дополнительная информация о пользователе
                        if user:
                            user_location = user.get("user_location", {})
                            if user_location:
                                location_name = user_location.get("name", "")
                                if location_name:
                                    self.stdout.write(f"   🌍 Откуда: {location_name}")
                else:
                    self.stdout.write("⚠️ Отзывы не найдены")

                # Показываем полную структуру первого отзыва для отладки
                if reviews:
                    self.stdout.write("\n🔍 СТРУКТУРА ПЕРВОГО ОТЗЫВА:")
                    first_review = reviews[0]
                    self.stdout.write(f"Ключи: {list(first_review.keys())}")

                    user_data = first_review.get("user", {})
                    if user_data:
                        self.stdout.write(f"User ключи: {list(user_data.keys())}")

            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ HTTP Error: {response.status_code}")
                )
                self.stdout.write(f"Response: {response.text}")

                # Специальные сообщения для частых ошибок
                if response.status_code == 400:
                    self.stdout.write(
                        "💡 Возможно неправильный location_id или параметры запроса"
                    )
                elif response.status_code == 401:
                    self.stdout.write(
                        "💡 Проблема с API ключом - проверьте его валидность"
                    )
                elif response.status_code == 403:
                    self.stdout.write("💡 API ключ не имеет доступа к этому endpoint")
                elif response.status_code == 429:
                    self.stdout.write("💡 Превышен лимит запросов - попробуйте позже")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Exception: {str(e)}"))

        # Дополнительные рекомендации
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("💡 РЕКОМЕНДАЦИИ:")
        self.stdout.write(
            "1. Убедитесь что API ключ активен и имеет доступ к Content API v1"
        )
        self.stdout.write("2. Проверьте лимиты вашего API плана")
        self.stdout.write(
            f"3. Location ID {location_id} должен существовать в TripAdvisor"
        )
        self.stdout.write(
            "4. Если отзывов мало, возможно бизнес новый или мало отзывов"
        )
        self.stdout.write("5. Попробуйте увеличить limit в параметрах запроса")
