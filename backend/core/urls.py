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
    
    # ТУРЫ - возвращаем все статические туры в core
    path("tours/", views.tours, name="tours"),
    path("tours/wine-tours/", views.wine_tours, name="wine_tours"),
    path("tours/milano-tours/", views.milano_tours, name="milano_tours"),
    path("tours/como-tours/", views.como_tours, name="como_tours"),
    
    # Отдельные туры
    path("tours/alba-barolo-tour/", views.alba_barolo_tour, name="alba_barolo_tour"),
    path("tours/barolo-barbaresco-from-milan/", views.barolo_barbaresco_from_milan, name="barolo_barbaresco_from_milan"),
    path("tours/como-city-walking-tour/", views.como_city_walking_tour, name="como_city_walking_tour"),
    path("tours/kick-off-walking-tour-in-milano/", views.kick_off_walking_tour_in_milano, name="kick_off_walking_tour_in_milano"),
    path("tours/lake-como-and-lugano-tour/", views.lake_como_and_lugano_tour, name="lake_como_and_lugano_tour"),
    path("tours/bellagio-varenna-tour/", views.bellagio_varenna_tour, name="bellagio_varenna_tour"),
    path("tours/lake-como-lugano-morcote-tour/", views.lake_como_lugano_morcote_tour, name="lake_como_lugano_morcote_tour"),
    
    # БЛОГ СТАТЬИ (статические)
    path("lake-como-day-trip/", views.lake_como_day_trip, name="lake_como_day_trip"),
    path("bernina-express-tour/", views.bernina_express_tour, name="bernina_express_tour"),
    path("bernina-express-video/", views.bernina_express_video, name="bernina_express_video"),
]
