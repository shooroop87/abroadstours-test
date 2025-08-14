# backend/tours/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'tours'

urlpatterns = [
    # Главная страница туров (список всех туров)
    path('', views.TourListView.as_view(), name='list'),
    
    # Категории туров
    path('category/<slug:slug>/', views.TourCategoryView.as_view(), name='category'),
    
    # AJAX для похожих туров
    path('ajax/similar/<int:tour_id>/', views.get_similar_tours, name='ajax_similar'),
    
    # Детальная страница тура (должна быть в конце!)
    path('<slug:slug>/', views.TourDetailView.as_view(), name='detail'),
]

# Добавляем обслуживание медиа файлов в DEBUG режиме
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
