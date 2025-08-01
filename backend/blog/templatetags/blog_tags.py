# backend/blog/templatetags/blog_tags.py
from django import template
from django.utils.safestring import mark_safe
from blog.models import BlogPost, Category
import re

register = template.Library()

@register.inclusion_tag('blog/widgets/popular_posts.html')
def popular_posts(limit=5):
    """Популярные статьи"""
    posts = BlogPost.objects.filter(
        status='published'
    ).order_by('-views_count')[:limit]
    return {'posts': posts}

@register.inclusion_tag('blog/widgets/recent_posts.html')
def recent_posts(limit=5):
    """Последние статьи"""
    posts = BlogPost.objects.filter(
        status='published'
    ).order_by('-published_at')[:limit]
    return {'posts': posts}

@register.inclusion_tag('blog/widgets/categories.html')
def blog_categories():
    """Категории блога"""
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}

@register.filter
def reading_time(content):
    """Подсчет времени чтения"""
    if not content:
        return 1
    
    # Удаляем HTML теги
    clean_content = re.sub(r'<[^>]+>', '', content)
    word_count = len(clean_content.split())
    
    # 200 слов в минуту
    time = max(1, round(word_count / 200))
    return time

@register.filter
def truncate_words_html(value, length):
    """Обрезка HTML контента по словам"""
    if not value:
        return ''
    
    # Удаляем HTML для подсчета слов
    clean_text = re.sub(r'<[^>]+>', '', value)
    words = clean_text.split()
    
    if len(words) <= length:
        return mark_safe(value)
    
    # Обрезаем и добавляем ...
    truncated = ' '.join(words[:length])
    return mark_safe(f"{truncated}...")

@register.simple_tag
def blog_post_url(post, language=None):
    """URL статьи с учетом языка"""
    if language:
        # Активируем нужный язык
        from django.utils import translation
        with translation.override(language):
            return post.get_absolute_url()
    return post.get_absolute_url()

@register.simple_tag(takes_context=True)
def blog_pagination_url(context, page_number):
    """URL для пагинации с сохранением параметров"""
    request = context['request']
    params = request.GET.copy()
    params['page'] = page_number
    return f"{request.path}?{params.urlencode()}"
