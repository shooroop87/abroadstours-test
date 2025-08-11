# blog/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils.translation import get_language
from django.core.paginator import Paginator
from .models import BlogPost, Category


class BlogListView(ListView):
    """Список всех статей блога"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        """Возвращаем только опубликованные статьи"""
        return BlogPost.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Blog - Abroads Tours'
        context['page_description'] = 'Travel tips, destination guides, and travel inspiration from Abroads Tours.'
        return context


class BlogDetailView(DetailView):
    """Детальная страница статьи"""
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'translations__slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Возвращаем только опубликованные статьи"""
        return BlogPost.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_object(self, queryset=None):
        """Получаем объект с правильной работой переводов"""
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get(self.slug_url_kwarg)
        if slug is None:
            raise Http404("No slug provided")
        
        try:
            # Ищем пост по slug в переводах
            obj = queryset.get(translations__slug=slug)
            
            # Увеличиваем счетчик просмотров
            obj.increment_views()
            
            return obj
            
        except BlogPost.DoesNotExist:
            raise Http404("Blog post not found")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Используем helper методы модели
        context['page_title'] = post.get_display_meta_title()
        context['page_description'] = post.get_display_meta_description()
        
        # Получаем связанные статьи
        context['related_posts'] = post.get_related_posts(limit=3)
        
        # Получаем предыдущую и следующую статьи
        context['next_post'] = post.get_next_post()
        context['previous_post'] = post.get_previous_post()
        
        # Получаем комментарии (только одобренные)
        context['comments'] = post.comments.filter(is_approved=True).order_by('-created_at')
        
        return context


class CategoryView(ListView):
    """Статьи определенной категории"""
    model = BlogPost
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.category = get_object_or_404(
            Category, 
            translations__slug=self.kwargs['slug'],
            is_active=True
        )
        return BlogPost.objects.filter(
            category=self.category,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['page_title'] = f"{self.category.safe_translation_getter('name', any_language=True)} - Blog"
        context['page_description'] = self.category.safe_translation_getter('description', any_language=True) or f"Articles in {self.category.safe_translation_getter('name', any_language=True)} category"
        return context


class TagView(ListView):
    """Статьи с определенным тегом"""
    model = BlogPost
    template_name = 'blog/tag.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.tag_slug = self.kwargs['slug']
        return BlogPost.objects.filter(
            tags__slug=self.tag_slug,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_slug'] = self.tag_slug
        context['page_title'] = f"#{self.tag_slug} - Blog"
        context['page_description'] = f"Articles tagged with {self.tag_slug}"
        return context


class SearchView(ListView):
    """Поиск по статьям"""
    model = BlogPost
    template_name = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return BlogPost.objects.filter(
                translations__title__icontains=query,
                status='published'
            ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
        return BlogPost.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['page_title'] = f"Search results for '{context['query']}'"
        context['page_description'] = f"Search results for {context['query']}"
        return context
