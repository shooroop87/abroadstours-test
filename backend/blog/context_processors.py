# backend/blog/context_processors.py
from django.core.exceptions import AppRegistryNotReady

def blog_context(request):
    """Контекстный процессор для блога"""
    try:
        from .models import Category, BlogPost
        
        return {
            'blog_categories': Category.objects.filter(is_active=True)[:10],
            'latest_posts': BlogPost.objects.filter(status='published')[:5],
            'featured_posts': BlogPost.objects.filter(
                status='published', 
                is_featured=True
            )[:3],
        }
    except (ImportError, AppRegistryNotReady):
        # Если приложение еще не готово или модели не найдены
        return {
            'blog_categories': [],
            'latest_posts': [],
            'featured_posts': [],
        }
