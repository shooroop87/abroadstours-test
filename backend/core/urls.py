# backend/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы
    path("", views.index, name="index"),
    path("load-more-reviews/", views.load_more_reviews, name="load_more_reviews"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    
    # Главная страница туров (перенаправляет на tours app)
    path("tours/", views.tours, name="tours"),
    
    # БЛОГ СТАТЬИ
    path("lake-como-day-trip/", views.lake_como_day_trip, name="lake_como_day_trip"),
    path("bernina-express-tour/", views.bernina_express_tour, name="bernina_express_tour"),
    path("bernina-express-video/", views.bernina_express_video, name="bernina_express_video"),
]
