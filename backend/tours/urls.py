# backend/tours/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from core import views as core_views  # Импортируем views из core

# БЕЗ app_name - это важно!
# app_name = 'tours'  # ЗАКОММЕНТИРОВАНО ИЛИ УДАЛЕНО

urlpatterns = [
    # Главная страница туров (список всех туров)
    path('', views.TourListView.as_view(), name='tour_list'),
    
    # СТАТИЧНЫЕ КАТЕГОРИИ ТУРОВ (из core)
    path('wine-tours/', core_views.wine_tours, name='wine_tours'),
    path('milano-tours/', core_views.milano_tours, name='milano_tours'),
    path('como-tours/', core_views.como_tours, name='como_tours'),
    
    # СТАТИЧНЫЕ ОТДЕЛЬНЫЕ ТУРЫ (из core) - ДОЛЖНЫ БЫТЬ ПЕРЕД ДИНАМИЧЕСКИМИ!
    path(
        'barolo-wine-tasting-tour-from-milan-alba/',
        core_views.alba_barolo_tour,
        name='alba_barolo_tour',
    ),
    path(
        'barolo-barbaresco-wine-tasting-from-milan-visit-alba/',
        core_views.barolo_barbaresco_from_milan,
        name='barolo_barbaresco_from_milan',
    ),
    path(
        'kick-off-walking-tour-in-milano/',
        core_views.kick_off_walking_tour_in_milano,
        name='kick_off_walking_tour_in_milano',
    ),
    path(
        'como-city-walking-tour-with-the-boat-cruise-small-group-tour/',
        core_views.como_city_walking_tour,
        name='como_city_walking_tour',
    ),
    path(
        'lake-como-and-lugano-small-group-tour-from-milan/',
        core_views.lake_como_and_lugano_tour,
        name='lake_como_and_lugano_tour',
    ),
    path(
        'bellagio-varenna-from-milan/',
        core_views.bellagio_varenna_tour,
        name='bellagio_varenna_tour',
    ),
    path(
        'from-milan-lake-como-and-lugano-tour-with-morcote/',
        core_views.lake_como_lugano_morcote_tour,
        name='lake_como_lugano_morcote_tour',
    ),
    
    # AJAX для похожих туров
    path('ajax/similar/<int:tour_id>/', views.get_similar_tours, name='ajax_similar_tours'),
    
    # ДИНАМИЧЕСКИЕ КАТЕГОРИИ ТУРОВ
    path('category/<slug:slug>/', views.TourCategoryView.as_view(), name='tour_category'),
    
    # ДИНАМИЧЕСКАЯ ДЕТАЛЬНАЯ СТРАНИЦА ТУРА (ДОЛЖНА БЫТЬ ПОСЛЕДНЕЙ!)
    path('<slug:slug>/', views.TourDetailView.as_view(), name='tour_detail'),
]

# Добавляем обслуживание медиа файлов в DEBUG режиме
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)