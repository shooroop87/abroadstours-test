# flake8: noqa
import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check if we are using correct business IDs for APIs"

    def handle(self, *args, **options):
        self.stdout.write("🔍 ПРОВЕРКА ID БИЗНЕСА")
        self.stdout.write("=" * 40)

        # Проверяем Google Place ID
        self.check_google_place_id()

        # Проверяем TripAdvisor поиск
        self.check_tripadvisor_search()

    def check_google_place_id(self):
        """Проверяем Google Place ID"""
        self.stdout.write("\n🔵 GOOGLE PLACES API:")
        self.stdout.write("-" * 25)

        api_key = getattr(settings, "GOOGLE_PLACES_API_KEY", "")
        place_id = getattr(settings, "GOOGLE_PLACE_ID", "")

        self.stdout.write(
            f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ No API key"
        )
        self.stdout.write(f"🆔 Place ID: {place_id}" if place_id else "❌ No Place ID")

        if api_key and place_id:
            # Получаем детали места
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,rating,user_ratings_total,reviews",
                "key": api_key,
            }

            try:
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("status") == "OK":
                        result = data.get("result", {})
                        name = result.get("name", "Unknown")
                        address = result.get("formatted_address", "Unknown")
                        rating = result.get("rating", "N/A")
                        total_reviews = result.get("user_ratings_total", 0)
                        reviews = result.get("reviews", [])

                        self.stdout.write(f"✅ Найден бизнес:")
                        self.stdout.write(f"   📍 Название: {name}")
                        self.stdout.write(f"   🏠 Адрес: {address}")
                        self.stdout.write(f"   ⭐ Рейтинг: {rating}")
                        self.stdout.write(f"   📊 Всего отзывов: {total_reviews}")
                        self.stdout.write(f"   📝 Получено отзывов: {len(reviews)}")

                        if reviews:
                            self.stdout.write("\n📋 Последние отзывы:")
                            for i, review in enumerate(reviews[:3], 1):
                                author = review.get("author_name", "Unknown")
                                text = review.get("text", "")[:60] + "..."
                                time_desc = review.get(
                                    "relative_time_description", "Unknown"
                                )
                                self.stdout.write(
                                    f"   {i}. {author} ({time_desc}): {text}"
                                )
                    else:
                        self.stdout.write(f'❌ Google API Error: {data.get("status")}')
                        if data.get("error_message"):
                            self.stdout.write(f'   💬 {data.get("error_message")}')
                else:
                    self.stdout.write(f"❌ HTTP Error: {response.status_code}")

            except Exception as e:
                self.stdout.write(f"💥 Exception: {str(e)}")

    def check_tripadvisor_search(self):
        """Проверяем поиск в TripAdvisor"""
        self.stdout.write("\n🟢 TRIPADVISOR API:")
        self.stdout.write("-" * 25)

        api_key = getattr(settings, "TRIPADVISOR_API_KEY", "")
        self.stdout.write(f"🔑 API Key: {api_key}")

        if not api_key:
            self.stdout.write("❌ No TripAdvisor API key")
            return

        # Поиск по разным запросам
        search_queries = [
            "Abroads Tours",
            "Abroads Tours Milan",
            "Milan day trips Abroads",
            "Lake Como tours Milan",
        ]

        for query in search_queries:
            self.stdout.write(f'\n🔍 Поиск: "{query}"')

            url = "https://api.content.tripadvisor.com/api/v1/location/search"
            params = {"key": api_key, "searchQuery": query, "language": "en"}

            try:
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("data", [])

                    if results:
                        self.stdout.write(f"   ✅ Найдено: {len(results)} результатов")

                        for i, result in enumerate(results[:2], 1):
                            name = result.get("name", "Unknown")
                            location_id = result.get("location_id", "N/A")
                            address = result.get("address_obj", {}).get(
                                "address_string", "N/A"
                            )

                            self.stdout.write(f"   {i}. {name}")
                            self.stdout.write(f"      🆔 ID: {location_id}")
                            self.stdout.write(f"      🏠 Адрес: {address}")

                            # Если это первый результат, проверим отзывы
                            if i == 1:
                                self.check_tripadvisor_reviews(
                                    api_key, location_id, name
                                )
                    else:
                        self.stdout.write("   ❌ Результатов не найдено")
                else:
                    self.stdout.write(f"   ❌ HTTP Error: {response.status_code}")

            except Exception as e:
                self.stdout.write(f"   💥 Exception: {str(e)}")

    def check_tripadvisor_reviews(self, api_key, location_id, business_name):
        """Проверяем отзывы для конкретной локации TripAdvisor"""
        self.stdout.write(f'\n      📝 Отзывы для "{business_name}":')

        url = (
            f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/reviews"
        )
        params = {"key": api_key, "language": "en", "limit": 3}

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                reviews = data.get("data", [])

                if reviews:
                    self.stdout.write(f"         ✅ Найдено: {len(reviews)} отзывов")

                    for j, review in enumerate(reviews, 1):
                        author = review.get("user", {}).get("username", "Unknown")
                        text = review.get("text", "")[:50] + "..."
                        date = review.get("published_date", "Unknown")

                        self.stdout.write(f"         {j}. {author} ({date}): {text}")
                else:
                    self.stdout.write("         ❌ Отзывов не найдено")
            else:
                self.stdout.write(f"         ❌ Reviews Error: {response.status_code}")

        except Exception as e:
            self.stdout.write(f"         💥 Reviews Exception: {str(e)}")
