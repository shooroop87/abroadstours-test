# blog/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Импортируем views из core для старых статических статей
from core import views as core_views

app_name = 'blog'

urlpatterns = [
    # Главная страница блога
    path('', views.BlogListView.as_view(), name='blog'),
    
    # Добавляем алиас для совместимости
    path('list/', views.BlogListView.as_view(), name='blog_list'),
    
    # Поиск - используем SearchView класс
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Категории - используем CategoryView класс
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    
    # Теги - используем TagView класс
    path('tag/<slug:slug>/', views.TagView.as_view(), name='tag'),
    
    # СТАТИЧЕСКИЕ СТАТЬИ ДЛЯ SEO СОВМЕСТИМОСТИ (ПЕРЕД динамическими!)
    path('lake-como-day-trip-from-milan-insiders-guide/',
         core_views.lake_como_day_trip,
         name='lake_como_day_trip'),
    path('a-bold-guide-to-bernina-express-tour-from-milan/',
         core_views.bernina_express_tour,
         name='bernina_express_tour'),
    path('watch-the-bernina-express-ride/',
         core_views.bernina_express_video,
         name='bernina_express_video'),
    
    # Динамические статьи (новая система) - должно быть в конце!
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='post_detail'),
]

# Добавляем обслуживание медиа файлов в DEBUG режиме
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
