# backend/blog/context_processors.py
from .models import Category, BlogPost

def blog_context(request):
    """Контекстный процессор для блога"""
    return {
        'blog_categories': Category.objects.filter(is_active=True)[:10],
        'latest_posts': BlogPost.objects.filter(status='published')[:5],
        'featured_posts': BlogPost.objects.filter(
            status='published', 
            is_featured=True
        )[:3],
    }
