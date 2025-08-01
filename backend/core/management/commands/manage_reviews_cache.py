# flake8: noqa
import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test TripAdvisor API connection and debug issues"

    def handle(self, *args, **options):
        api_key = getattr(settings, "TRIPADVISOR_API_KEY", "")

        self.stdout.write(
            f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ No API key found"
        )

        if not api_key:
            self.stdout.write(self.style.ERROR("❌ TripAdvisor API key not configured"))
            return

        self.stdout.write("\n🔍 Testing location search...")

        search_url = "https://api.content.tripadvisor.com/api/v1/location/search"
        search_params = {
            "key": api_key,
            "searchQuery": "Abroads Tours Milan",
            "category": "attractions",
            "language": "en",
        }

        try:
            self.stdout.write(f"📡 Making request to: {search_url}")
            self.stdout.write(f"📝 Parameters: {search_params}")

            response = requests.get(search_url, params=search_params, timeout=15)

            self.stdout.write(f"📊 Status Code: {response.status_code}")
            self.stdout.write(f"📋 Headers: {dict(response.headers)}")

            if response.status_code == 200:
                data = response.json()
                self.stdout.write(f"✅ Response: {data}")

                if data.get("data"):
                    location_id = data["data"][0]["location_id"]
                    self.stdout.write(f"🎯 Found location ID: {location_id}")
                    self.test_reviews(api_key, location_id)
                else:
                    self.stdout.write('⚠️ No locations found for "Abroads Tours Milan"')
                    self.try_alternative_searches(api_key)
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ HTTP Error: {response.status_code}")
                )
                self.stdout.write(f"Response: {response.text}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Exception: {str(e)}"))

    def test_reviews(self, api_key, location_id):
        self.stdout.write(f"\n📝 Testing reviews for location {location_id}...")

        reviews_url = (
            f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/reviews"
        )
        reviews_params = {
            "key": api_key,
            "language": "en",
            "limit": 5,
        }

        try:
            response = requests.get(reviews_url, params=reviews_params, timeout=15)
            self.stdout.write(f"📊 Reviews Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                reviews_count = len(data.get("data", []))
                self.stdout.write(f"✅ Found {reviews_count} reviews")

                if reviews_count > 0:
                    first_review = data["data"][0]
                    self.stdout.write("📄 Sample review:")
                    author = first_review.get("user", {}).get("username", "N/A")
                    rating = first_review.get("rating", "N/A")
                    text = first_review.get("text", "N/A")

                    self.stdout.write(f"   Author: {author}")
                    self.stdout.write(f"   Rating: {rating}")
                    self.stdout.write(f"   Text: {text[:100]}...")
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Reviews HTTP Error: {response.status_code}")
                )
                self.stdout.write(f"Response: {response.text}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 Reviews Exception: {str(e)}"))

    def try_alternative_searches(self, api_key):
        self.stdout.write("\n🔄 Trying alternative search queries...")

        alternative_queries = [
            "Milan tour guide",
            "Milan day trips",
            "Lake Como tours Milan",
            "Milan tours",
            "Abroads Tours",
        ]

        for query in alternative_queries:
            self.stdout.write(f'\n🔍 Searching for: "{query}"')

            search_params = {
                "key": api_key,
                "searchQuery": query,
                "category": "attractions",
                "language": "en",
            }

            try:
                response = requests.get(
                    "https://api.content.tripadvisor.com/api/v1/location/search",
                    params=search_params,
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()
                    results_count = len(data.get("data", []))
                    self.stdout.write(f"   ✅ Found {results_count} results")

                    if results_count > 0:
                        for i, result in enumerate(data["data"][:3]):
                            name = result.get("name", "N/A")
                            location_id = result.get("location_id", "N/A")
                            self.stdout.write(f"   {i + 1}. {name} (ID: {location_id})")
                else:
                    self.stdout.write(f"   ❌ Error: {response.status_code}")

            except Exception as e:
                self.stdout.write(f"   💥 Exception: {str(e)}")
