# flake8: noqa
import logging
from datetime import datetime
from operator import itemgetter

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class MultiSourceReviewsService:
    """
    Сервис для получения отзывов из нескольких источников:
    1. TripAdvisor Content API (приоритет)
    2. Google Places API (резерв)
    3. Fallback отзывы (если все API недоступны)
    """

    def __init__(self):
        self.tripadvisor_api_key = getattr(settings, "TRIPADVISOR_API_KEY", "")
        # TripAdvisor location ID для вашего бизнеса
        self.tripadvisor_location_id = "24938712"  # Ваш правильный ID

        self.google_api_key = getattr(settings, "GOOGLE_PLACES_API_KEY", "")
        self.google_place_id = getattr(settings, "GOOGLE_PLACE_ID", "")
        self.cache_timeout = getattr(settings, "REVIEWS_CACHE_TIMEOUT", 21600)

    def get_reviews(self, page=1, per_page=7):
        cache_key = f"multi_reviews_page_{page}_{per_page}"
        cached_reviews = cache.get(cache_key)
        if cached_reviews is not None:
            logger.info(f"Reviews page {page} loaded from cache")
            return cached_reviews

        all_reviews = self._fetch_all_reviews()

        if not all_reviews:
            return self._get_fallback_response(page, per_page)

        sorted_reviews = sorted(all_reviews, key=itemgetter("timestamp"), reverse=True)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_reviews = sorted_reviews[start_idx:end_idx]

        # Нормализуем данные для шаблона
        normalized_reviews = []
        for review in page_reviews:
            normalized_review = {
                "review_id": review.get("id", ""),
                "author_name": review.get("author", "Anonymous"),
                "author_photo_url": review.get("author_photo", ""),
                "rating": int(review.get("rating", 5)),
                "text": review.get("text", ""),
                "relative_time_description": self._format_relative_time(
                    review.get("timestamp", 0)
                ),
                "source": review.get("source", "unknown"),
            }
            normalized_reviews.append(normalized_review)

        response_data = {
            "reviews": normalized_reviews,
            "page": page,
            "per_page": per_page,
            "total_reviews": len(sorted_reviews),
            "has_next": end_idx < len(sorted_reviews),
            "sources_used": self._get_sources_status(),
            "fetched_at": datetime.now().isoformat(),
        }

        cache.set(cache_key, response_data, self.cache_timeout)
        logger.info(
            f"Reviews page {page} fetched and cached with {len(normalized_reviews)} reviews"
        )
        return response_data

    def _fetch_all_reviews(self):
        all_reviews = []

        # Сначала пробуем TripAdvisor Content API
        try:
            tripadvisor_reviews = self._fetch_tripadvisor_reviews()
            if tripadvisor_reviews:
                all_reviews.extend(tripadvisor_reviews)
                logger.info(
                    f"Fetched {len(tripadvisor_reviews)} reviews from TripAdvisor"
                )
        except Exception as e:
            logger.error(f"TripAdvisor fetch failed: {str(e)}")

        # Затем Google Places API
        try:
            google_reviews = self._fetch_google_reviews()
            if google_reviews:
                all_reviews.extend(google_reviews)
                logger.info(f"Fetched {len(google_reviews)} reviews from Google")
        except Exception as e:
            logger.error(f"Google fetch failed: {str(e)}")

        return all_reviews

    def _fetch_tripadvisor_reviews(self):
        """Fetch reviews from TripAdvisor Content API v1"""
        if not self.tripadvisor_api_key:
            logger.warning("TripAdvisor API key not configured")
            return []

        try:
            # Используем правильный Content API v1
            url = f"https://api.content.tripadvisor.com/api/v1/location/{self.tripadvisor_location_id}/reviews"

            params = {
                "key": self.tripadvisor_api_key,
                "language": "en",
                "limit": 20,  # Максимум отзывов за запрос
            }

            headers = {
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; AbroadsTours/1.0)",
            }

            logger.info(f"Fetching TripAdvisor reviews from: {url}")
            logger.info(f"Using location_id: {self.tripadvisor_location_id}")

            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()

            data = response.json()
            logger.info(f"TripAdvisor API response status: {response.status_code}")
            logger.info(f"TripAdvisor raw response: {data}")

            return self._normalize_tripadvisor_reviews(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"TripAdvisor API request failed: {str(e)}")
            return []
        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"TripAdvisor response parsing failed: {str(e)}")
            return []

    def _fetch_google_reviews(self):
        """Fetch reviews from Google Places API with detailed fields"""
        if not (self.google_api_key and self.google_place_id):
            logger.warning("Google Places API credentials not configured")
            return []

        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"

            # Запрашиваем больше полей для получения полной информации
            params = {
                "place_id": self.google_place_id,
                "fields": "reviews,rating,user_ratings_total,name,formatted_address",
                "key": self.google_api_key,
                "language": "en",
            }

            logger.info(f"Fetching Google reviews for place_id: {self.google_place_id}")

            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Google API response status: {response.status_code}")

            if data.get("status") != "OK":
                logger.error(
                    f"Google API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}"
                )
                return []

            result = data.get("result", {})
            business_name = result.get("name", "Unknown")
            business_address = result.get("formatted_address", "Unknown")
            total_reviews = result.get("user_ratings_total", 0)

            logger.info(f"Google business found: {business_name} at {business_address}")
            logger.info(f"Total Google reviews available: {total_reviews}")

            return self._normalize_google_reviews(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Google Places API request failed: {str(e)}")
            return []
        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"Google Places response parsing failed: {str(e)}")
            return []

    def _normalize_tripadvisor_reviews(self, data):
        """Normalize TripAdvisor Content API v1 review data"""
        try:
            reviews = data.get("data", [])

            if not reviews:
                logger.warning("No TripAdvisor reviews found in response")
                return []

            normalized = []
            for review in reviews:
                try:
                    # TripAdvisor Content API v1 структура
                    user_info = review.get("user", {})

                    normalized_review = {
                        "id": f"ta_{review.get('id', hash(review.get('text', '')))}",
                        "author": user_info.get("username", "TripAdvisor User"),
                        "author_photo": user_info.get("avatar", {}).get("small", ""),
                        "rating": int(review.get("rating", 5)),
                        "text": review.get("text", "").strip(),
                        "timestamp": self._parse_tripadvisor_date(
                            review.get("published_date", "")
                        ),
                        "source": "tripadvisor",
                        "title": review.get("title", ""),
                        "language": review.get("language", "en"),
                    }

                    if normalized_review["text"]:  # Только отзывы с текстом
                        normalized.append(normalized_review)
                        logger.debug(
                            f"Normalized TripAdvisor review from {normalized_review['author']}"
                        )

                except Exception as e:
                    logger.warning(
                        f"Error processing individual TripAdvisor review: {str(e)}"
                    )
                    continue

            logger.info(
                f"Successfully normalized {len(normalized)} TripAdvisor reviews"
            )
            return normalized

        except Exception as e:
            logger.error(f"Error normalizing TripAdvisor reviews: {str(e)}")
            return []

    def _normalize_google_reviews(self, data):
        """Normalize Google Places review data with better author handling"""
        try:
            result = data.get("result", {})
            reviews = result.get("reviews", [])

            if not reviews:
                logger.warning("No Google reviews found in response")
                return []

            normalized = []
            for review in reviews:
                try:
                    # Google возвращает author_name и profile_photo_url
                    author_name = review.get("author_name", "Google User")
                    author_photo = review.get("profile_photo_url", "")

                    # Если автор не указан, используем первую букву из текста отзыва
                    if not author_name or author_name == "A Google User":
                        author_name = "Google User"

                    normalized_review = {
                        "id": f"google_{review.get('time', hash(review.get('text', '')))}",
                        "author": author_name,
                        "author_photo": author_photo,
                        "rating": int(review.get("rating", 5)),
                        "text": review.get("text", "").strip(),
                        "timestamp": self._parse_google_timestamp(
                            review.get("time", 0)
                        ),
                        "source": "google",
                        "title": "",
                        "language": review.get("language", "en"),
                    }

                    if normalized_review["text"]:  # Только отзывы с текстом
                        normalized.append(normalized_review)
                        logger.debug(f"Normalized Google review from {author_name}")

                except Exception as e:
                    logger.warning(
                        f"Error processing individual Google review: {str(e)}"
                    )
                    continue

            logger.info(f"Successfully normalized {len(normalized)} Google reviews")
            return normalized

        except Exception as e:
            logger.error(f"Error normalizing Google reviews: {str(e)}")
            return []

    def _format_relative_time(self, timestamp):
        """Format timestamp to relative time description"""
        try:
            review_time = datetime.fromtimestamp(float(timestamp))
            now = datetime.now()
            diff = now - review_time

            days = diff.days
            hours = diff.seconds // 3600

            if days == 0:
                if hours == 0:
                    return "Today"
                elif hours == 1:
                    return "1 hour ago"
                else:
                    return f"{hours} hours ago"
            elif days == 1:
                return "1 day ago"
            elif days < 7:
                return f"{days} days ago"
            elif days < 30:
                weeks = days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif days < 365:
                months = days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"

        except (ValueError, TypeError):
            return "Recently"

    def _parse_tripadvisor_date(self, date_str):
        """Parse TripAdvisor date string to timestamp"""
        try:
            if not date_str:
                return datetime.now().timestamp()

            # TripAdvisor Content API v1 обычно возвращает ISO формат
            date_formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO with microseconds
                "%Y-%m-%dT%H:%M:%SZ",  # ISO without microseconds
                "%Y-%m-%d",  # Simple date
            ]

            for fmt in date_formats:
                try:
                    dt = datetime.strptime(
                        date_str.replace("Z", ""), fmt.replace("Z", "")
                    )
                    return dt.timestamp()
                except ValueError:
                    continue

            logger.warning(f"Unknown TripAdvisor date format: {date_str}")
            return datetime.now().timestamp()

        except (ValueError, TypeError):
            return datetime.now().timestamp()

    def _parse_google_timestamp(self, timestamp):
        """Parse Google timestamp (Unix timestamp)"""
        try:
            return float(timestamp)
        except (ValueError, TypeError):
            return datetime.now().timestamp()

    def _get_sources_status(self):
        """Get status of configured API sources"""
        return {
            "tripadvisor": bool(self.tripadvisor_api_key),
            "google": bool(self.google_api_key and self.google_place_id),
        }

    def clear_cache(self):
        """Clear all cached reviews"""
        for page in range(1, 11):
            for per_page in [7, 30]:
                cache_key = f"multi_reviews_page_{page}_{per_page}"
                cache.delete(cache_key)
        logger.info("Multi-source reviews cache cleared")

    def _get_fallback_response(self, page, per_page):
        """Return fallback response when no API data available"""
        fallback_reviews = self._get_fallback_reviews()

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_reviews = fallback_reviews[start_idx:end_idx]

        return {
            "reviews": page_reviews,
            "page": page,
            "per_page": per_page,
            "total_reviews": len(fallback_reviews),
            "has_next": end_idx < len(fallback_reviews),
            "sources_used": {"fallback": True},
            "fetched_at": datetime.now().isoformat(),
            "fallback_mode": True,
        }

    def _get_fallback_reviews(self):
        """Return static fallback reviews with proper format for template"""
        current_time = datetime.now().timestamp()

        fallback_data = [
            {
                "id": "fallback_1",
                "author": "Marco R.",
                "rating": 5,
                "text": "We had an absolutely delightful time on our tour of Lake Como and into Switzerland up to Lugano. It was especially nice to not be on a large bus and to have personal attention from our guide.",
                "timestamp": current_time - 86400,  # 1 day ago
                "source": "fallback",
            },
            {
                "id": "fallback_2",
                "author": "Sarah J.",
                "rating": 5,
                "text": "Stefano was great, friendly, easy to converse with & very informative! With the small group, Stefano gave us options to stay longer or shorter in each location.",
                "timestamp": current_time - 172800,  # 2 days ago
                "source": "fallback",
            },
            {
                "id": "fallback_3",
                "author": "Monica K.",
                "rating": 5,
                "text": "We had a wonderful time on this tour. Our guide Monica showed our small group so many local places we really got to enjoy each location.",
                "timestamp": current_time - 259200,  # 3 days ago
                "source": "fallback",
            },
            {
                "id": "fallback_4",
                "author": "Travel Enthusiast",
                "rating": 5,
                "text": "Great excursion to Como and Lugano! Very well planned, small group, pleasant journeys by Swiss train and boat, very good food for lunch.",
                "timestamp": current_time - 345600,  # 4 days ago
                "source": "fallback",
            },
            {
                "id": "fallback_5",
                "author": "Happy Traveler",
                "rating": 5,
                "text": "The Lake Como Tour (Milan -> Varenna -> Bellagio -> Bellano -> Milan) was possibly the best part of my trip to Italy. Straight off, amazing experience!",
                "timestamp": current_time - 432000,  # 5 days ago
                "source": "fallback",
            },
        ]

        # Нормализуем fallback отзывы для шаблона
        normalized_fallback = []
        for review in fallback_data:
            normalized_review = {
                "review_id": review["id"],
                "author_name": review["author"],
                "author_photo_url": "",
                "rating": review["rating"],
                "text": review["text"],
                "relative_time_description": self._format_relative_time(
                    review["timestamp"]
                ),
                "source": review["source"],
            }
            normalized_fallback.append(normalized_review)

        return normalized_fallback
