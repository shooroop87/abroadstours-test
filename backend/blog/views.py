# backend/blog/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import BlogPost, Category
from taggit.models import Tag


class BlogListView(ListView):
    """Список всех статей блога"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['page_title'] = 'Blog'
        return context


class BlogDetailView(DetailView):
    """Детальная страница статьи"""
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров
        obj.increment_views()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Похожие статьи
        context['related_posts'] = post.get_related_posts()
        
        # Комментарии
        context['comments'] = post.comments.filter(is_approved=True).order_by('-created_at')
        
        context['page_title'] = post.safe_translation_getter('title', any_language=True)
        return context


class CategoryListView(ListView):
    """Статьи по категории"""
    model = BlogPost
    template_name = 'blog/category_detail.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.category = get_object_or_404(
            Category, 
            slug=self.kwargs['slug'], 
            is_active=True
        )
        return BlogPost.objects.filter(
            category=self.category, 
            status='published'
        ).order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['page_title'] = f'Category: {self.category.safe_translation_getter("name", any_language=True)}'
        return context


def tag_posts(request, tag_slug):
    """Статьи по тегу"""
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = BlogPost.objects.filter(
        tags__in=[tag], 
        status='published'
    ).order_by('-published_at')
    
    # Пагинация
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'posts': page_obj,
        'page_title': f'Tag: {tag.name}',
    }
    
    return render(request, 'blog/tag_posts.html', context)


def blog_search(request):
    """Поиск по блогу"""
    query = request.GET.get('q', '')
    posts = []
    
    if query:
        posts = BlogPost.objects.filter(
            Q(translations__title__icontains=query) |
            Q(translations__content__icontains=query) |
            Q(translations__excerpt__icontains=query),
            status='published'
        ).distinct().order_by('-published_at')
    
    # Пагинация
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'query': query,
        'page_title': f'Search: {query}' if query else 'Search',
    }
    
    return render(request, 'blog/search_results.html', context)


# === ВАШИ СУЩЕСТВУЮЩИЕ СТАТИЧЕСКИЕ СТАТЬИ ===

def lake_como_day_trip(request):
    """Статическая статья - поездка на озеро Комо"""
    context = {
        'page_title': 'Lake Como Day Trip from Milan',
        'meta_description': 'Discover the beauty of Lake Como on a day trip from Milan',
    }
    return render(request, 'blog/static/lake_como_day_trip.html', context)


def bernina_express_tour(request):
    """Статическая статья - тур на Bernina Express"""
    context = {
        'page_title': 'Bernina Express Tour from Milan',
        'meta_description': 'Experience the scenic Bernina Express train journey from Milan',
    }
    return render(request, 'blog/static/bernina_express_tour.html', context)


def bernina_express_video(request):
    """Видео Bernina Express"""
    context = {
        'page_title': 'Watch Bernina Express Ride',
        'meta_description': 'Watch stunning videos of the Bernina Express train ride',
    }
    return render(request, 'blog/static/bernina_express_video.html', context)
