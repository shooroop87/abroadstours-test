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
   path("tours/", views.tours, name="tours"),
   
   # Категории туров
   path("tours/wine-tours/", views.wine_tours, name="wine_tours"),
   path("tours/milano-tours/", views.milano_tours, name="milano_tours"),
   path("tours/como-tours/", views.como_tours, name="como_tours"),
   
   # Отдельные туры
   path(
       "tours/barolo-wine-tasting-tour-from-milan-alba/",
       views.alba_barolo_tour,
       name="alba_barolo_tour",
   ),
   path(
       "tours/barolo-barbaresco-wine-tasting-from-milan-visit-alba/",
       views.barolo_barbaresco_from_milan,
       name="barolo_barbaresco_from_milan",
   ),
   path(
       "tours/kick-off-walking-tour-in-milano/",
       views.kick_off_walking_tour_in_milano,
       name="kick_off_walking_tour_in_milano",
   ),
   path(
       "tours/como-city-walking-tour-with-the-boat-cruise-small-group-tour/",
       views.como_city_walking_tour,
       name="como_city_walking_tour",
   ),
   path(
       "tours/lake-como-and-lugano-small-group-tour-from-milan/",
       views.lake_como_and_lugano_tour,
       name="lake_como_and_lugano_tour",
   ),
   path(
       "tours/bellagio-varenna-from-milan/",
       views.bellagio_varenna_tour,
       name="bellagio_varenna_tour",
   ),
   path(
       "tours/from-milan-lake-como-and-lugano-tour-with-morcote/",
       views.lake_como_lugano_morcote_tour,
       name="lake_como_lugano_morcote_tour",
   ),
   
   # Блог статьи (временно добавлены для исправления ошибок)
   path("lake-como-day-trip/", views.lake_como_day_trip, name="lake_como_day_trip"),
   path("bernina-express-tour/", views.bernina_express_tour, name="bernina_express_tour"),
   path("bernina-express-video/", views.bernina_express_video, name="bernina_express_video"),


   path("test-image/", views.test_image_view, name="test_image"),
]


