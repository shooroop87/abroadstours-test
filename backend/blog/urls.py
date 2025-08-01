# backend/blog/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'blog'

urlpatterns = [
    # Главная страница блога - это исправит NoReverseMatch для 'blog'
    path('', views.BlogListView.as_view(), name='blog'),  # ✅ Используем класс, а не функцию
    
    # Поиск
    path('search/', views.blog_search, name='search'),
    
    # Категории
    path('category/<slug:slug>/', views.CategoryListView.as_view(), name='category'),
    
    # Теги
    path('tag/<slug:tag_slug>/', views.tag_posts, name='tag'),
    
    # Статические статьи (ваши существующие)
    path('lake-como-day-trip-from-milan/', views.lake_como_day_trip, name='lake_como_day_trip'),
    path('bernina-express-tour-from-milan/', views.bernina_express_tour, name='bernina_express_tour'),
    path('watch-bernina-express-ride/', views.bernina_express_video, name='bernina_express_video'),
    
    # Динамические статьи (новая система) - должно быть в конце!
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='post_detail'),
]
