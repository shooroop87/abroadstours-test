import json

import requests
from django.conf import settings
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.utils.translation import activate
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_headers

from django.http import FileResponse, Http404
import os

# Импортируем только сервис отзывов
from .services.multi_reviews_service import MultiSourceReviewsService


# --- SendPulse API ключи ---
SENDPULSE_CLIENT_ID = "your_client_id"
SENDPULSE_CLIENT_SECRET = "your_client_secret"
SENDPULSE_LIST_ID = "your_list_id"


def get_sendpulse_token():
    url = "https://api.sendpulse.com/oauth/access_token"
    data = {
        "grant_type": "client_credentials",
        "client_id": SENDPULSE_CLIENT_ID,
        "client_secret": SENDPULSE_CLIENT_SECRET,
    }
    res = requests.post(url, data=data)
    return res.json().get("access_token")


@csrf_exempt
def subscribe_to_newsletter(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"message": "Email is required"}, status=400)

            token = get_sendpulse_token()
            if not token:
                return JsonResponse({"message": "Authorization error"}, status=500)

            url = (
                f"https://api.sendpulse.com/addressbooks/" f"{SENDPULSE_LIST_ID}/emails"
            )
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"emails": [{"email": email}]}

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return JsonResponse({"message": "Successfully subscribed"})
            else:
                return JsonResponse({"message": "Subscription failed"}, status=400)

        except (
            json.JSONDecodeError,
            requests.exceptions.RequestException,
            KeyError,
            ValueError,
        ):
            return JsonResponse({"message": "Server error"}, status=500)

    return JsonResponse({"message": "Invalid request"}, status=405)


# --- ТОЛЬКО ДВА НОВЫХ ENDPOINT ДЛЯ ОТЗЫВОВ ---


@csrf_exempt
def load_more_reviews(request):
    """AJAX для подгрузки отзывов через стрелки слайдера"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 7))

        reviews_service = MultiSourceReviewsService()
        reviews_data = reviews_service.get_reviews(page=page, per_page=per_page)

        return JsonResponse(reviews_data)

    except (ValueError, TypeError, AttributeError):
        return JsonResponse({"error": "Error loading reviews"}, status=500)


# --- ЯЗЫК ---
def set_language(request):
    lang = request.GET.get("language")
    next_url = request.GET.get("next", "/")
    if lang in dict(settings.LANGUAGES):
        activate(lang)
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
    return HttpResponseRedirect("/")


# --- ОБНОВЛЕННАЯ ТОЛЬКО ГЛАВНАЯ СТРАНИЦА ---
@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def index(request):
    """Главная страница с отзывами"""
    try:
        reviews_service = MultiSourceReviewsService()
        reviews_data = reviews_service.get_reviews(page=1, per_page=7)

        context = {
            "reviews_data": reviews_data,
            "google_reviews": reviews_data.get("reviews", []),
        }
    except (AttributeError, TypeError, KeyError):
        # Fallback если API недоступны
        context = {
            "reviews_data": {"reviews": [], "has_next": False},
            "google_reviews": [],
        }

    return render(request, "pages/index.html", context)


# --- ВСЕ ОСТАЛЬНЫЕ СТРАНИЦЫ БЕЗ ИЗМЕНЕНИЙ ---
@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def contact(request):
    return render(request, "pages/contact.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def privacy_policy(request):
    return render(request, "pages/privacy_policy.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def about(request):
    return render(request, "pages/about.html")


# УБИРАЕМ СТАРУЮ ФУНКЦИЮ blog() - теперь блог управляется через новое приложение
# @cache_page(60 * 60 * 24)
# @vary_on_headers("Accept-Language")
# def blog(request):
#     return render(request, "pages/blog.html")


# --- СТАТИЧЕСКИЕ BLOG СТАТЬИ (СОХРАНЯЕМ ДЛЯ СОВМЕСТИМОСТИ) ---
@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def lake_como_day_trip(request):
    return render(request, "blog/lake-como-day-trip-from-milan-insiders-guide.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def bernina_express_tour(request):
    return render(request, "blog/a-bold-guide-to-bernina-express-tour-from-milan.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def bernina_express_video(request):
    return render(request, "blog/the-bernina-express-ride.html")


# --- ТУРЫ ---
@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def tours(request):
    return render(request, "pages/tour-list.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def wine_tours(request):
    return render(request, "pages/wine-tours.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def milano_tours(request):
    return render(request, "pages/milano-tours.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def como_tours(request):
    return render(request, "pages/como-tours.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def alba_barolo_tour(request):
    return render(request, "tours/alba_barolo.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def barolo_barbaresco_from_milan(request):
    return render(request, "tours/barolo_barbaresco_from_milan.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def como_city_walking_tour(request):
    return render(request, "tours/como_city_walking_tour.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def kick_off_walking_tour_in_milano(request):
    return render(request, "tours/kick-off-walking-tour-in-milano.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def lake_como_and_lugano_tour(request):
    return render(request, "tours/lake_como_and_lugano_tour.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def bellagio_varenna_tour(request):
    return render(request, "tours/bellagio_varenna_tour.html")


@cache_page(60 * 60 * 24)
@vary_on_headers("Accept-Language")
def lake_como_lugano_morcote_tour(request):
    return render(request, "tours/lake_como_lugano_morcote_tour.html")


# --- КАСТОМНЫЕ ОШИБКИ ---
def custom_404(request, exception):
    return render(request, "pages/404.html", status=404)


def custom_500(request):
    return render(request, "pages/500.html", status=500)


def test_image_view(request):
    # Проверим все возможные файлы
    files_to_check = [
        "/app/media/blog/featured/photo_5215488009007395914_y.jpg",
        "/app/media/blog/featured/photo_5215488009007395914_y_mDSsS6v.jpg"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
            except Exception as e:
                return HttpResponse(f"Error opening file: {e}", status=500)
    
    return HttpResponse("No image files found", status=404)
