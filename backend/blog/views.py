# blog/views.py
import logging
import os
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils.translation import get_language
from django.core.paginator import Paginator
from django.conf import settings
from .models import BlogPost, Category

# Настройка логгера
logger = logging.getLogger('blog')


class BlogListView(ListView):
    """Список всех статей блога с логированием"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        """Возвращаем только опубликованные статьи"""
        logger.info("📄 Получаем queryset для списка блога")
        
        queryset = BlogPost.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
        
        total_posts = queryset.count()
        logger.info(f"📄 Найдено опубликованных постов: {total_posts}")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Добавляем контекст с подробным логированием"""
        logger.info("🔧 Формируем контекст для BlogListView")
        
        context = super().get_context_data(**kwargs)
        posts = context.get('posts', [])
        
        logger.info(f"📄 Отображаем {len(posts)} постов на странице")
        
        # Детальный анализ каждого поста
        for i, post in enumerate(posts, 1):
            logger.info(f"📝 Пост {i}: ID={post.id}, Title='{post.get_display_title()}'")
            logger.info(f"   Status: {post.status}")
            logger.info(f"   Author: {post.author.username}")
            logger.info(f"   Published: {post.published_at}")
            
            # Подробная проверка изображения
            if post.featured_image:
                logger.info(f"🖼️ Пост {i} - есть featured_image:")
                logger.info(f"   Name: {post.featured_image.name}")
                logger.info(f"   URL: {post.featured_image.url}")
                
                # Проверяем физическое существование файла
                try:
                    image_path = post.featured_image.path
                    logger.info(f"   Path: {image_path}")
                    
                    if os.path.exists(image_path):
                        file_size = os.path.getsize(image_path)
                        logger.info(f"   ✅ Файл существует, размер: {file_size} bytes")
                        
                        # Проверяем права доступа
                        readable = os.access(image_path, os.R_OK)
                        logger.info(f"   🔒 Доступен для чтения: {readable}")
                        
                        # Проверяем, что это действительно изображение
                        try:
                            from PIL import Image
                            with Image.open(image_path) as img:
                                logger.info(f"   🖼️ Размеры: {img.width}x{img.height}, формат: {img.format}")
                        except Exception as img_e:
                            logger.error(f"   ❌ Ошибка при проверке изображения: {img_e}")
                    else:
                        logger.error(f"   ❌ Файл НЕ существует: {image_path}")
                        
                        # Проверяем директорию
                        dir_path = os.path.dirname(image_path)
                        if os.path.exists(dir_path):
                            logger.info(f"   📁 Директория существует: {dir_path}")
                            dir_contents = os.listdir(dir_path)
                            logger.info(f"   📁 Содержимое директории: {dir_contents}")
                        else:
                            logger.error(f"   📁 Директория НЕ существует: {dir_path}")
                            
                except Exception as e:
                    logger.error(f"   ❌ Ошибка при проверке пути изображения: {e}")
            else:
                logger.warning(f"❌ Пост {i} - НЕТ featured_image")
            
            # Проверяем категорию
            if post.category:
                category_name = post.category.safe_translation_getter('name', any_language=True)
                logger.info(f"   📂 Категория: {category_name}")
            else:
                logger.warning(f"   📂 Нет категории")
        
        # Добавляем отладочную информацию в контекст
        context['page_title'] = 'Blog - Abroads Tours'
        context['page_description'] = 'Travel tips, destination guides, and travel inspiration from Abroads Tours.'
        
        # Информация о медиа настройках
        context['debug_info'] = {
            'media_url': settings.MEDIA_URL,
            'media_root': settings.MEDIA_ROOT,
            'debug': settings.DEBUG,
            'total_posts': len(posts),
        }
        
        logger.info(f"🔧 Контекст сформирован успешно")
        logger.info(f"⚙️ MEDIA_URL: {settings.MEDIA_URL}")
        logger.info(f"⚙️ MEDIA_ROOT: {settings.MEDIA_ROOT}")
        logger.info(f"⚙️ DEBUG: {settings.DEBUG}")
        
        return context


class BlogDetailView(DetailView):
    """Детальная страница статьи с логированием"""
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'translations__slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Возвращаем только опубликованные статьи"""
        logger.info("📄 Получаем queryset для детальной страницы")
        
        queryset = BlogPost.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')
        
        logger.info(f"📄 Queryset для детальной страницы: {queryset.count()} постов")
        return queryset
    
    def get_object(self, queryset=None):
        """Получаем объект с правильной работой переводов"""
        logger.info("🔍 Поиск поста по slug")
        
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get(self.slug_url_kwarg)
        logger.info(f"🔍 Ищем пост с slug: '{slug}'")
        
        if slug is None:
            logger.error("❌ Slug не предоставлен")
            raise Http404("No slug provided")
        
        try:
            # Ищем пост по slug в переводах
            obj = queryset.get(translations__slug=slug)
            logger.info(f"✅ Пост найден: ID={obj.id}, Title='{obj.get_display_title()}'")
            
            # Проверяем изображение
            if obj.featured_image:
                logger.info(f"🖼️ У поста есть изображение: {obj.featured_image.url}")
                
                if os.path.exists(obj.featured_image.path):
                    logger.info(f"✅ Файл изображения существует")
                else:
                    logger.error(f"❌ Файл изображения НЕ существует: {obj.featured_image.path}")
            else:
                logger.warning("⚠️ У поста нет featured_image")
            
            # Увеличиваем счетчик просмотров
            logger.info("👁️ Увеличиваем счетчик просмотров")
            obj.increment_views()
            
            return obj
            
        except BlogPost.DoesNotExist:
            logger.error(f"❌ Пост с slug '{slug}' не найден")
            raise Http404("Blog post not found")
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске поста: {e}")
            raise
    
    def get_context_data(self, **kwargs):
        """Формируем контекст с логированием"""
        logger.info("🔧 Формируем контекст для детальной страницы")
        
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Используем helper методы модели
        context['page_title'] = post.get_display_meta_title()
        context['page_description'] = post.get_display_meta_description()
        
        logger.info(f"📄 Meta title: '{context['page_title']}'")
        logger.info(f"📄 Meta description: '{context['page_description']}'")
        
        # Получаем связанные статьи
        logger.info("🔗 Получаем связанные статьи")
        related_posts = post.get_related_posts(limit=3)
        context['related_posts'] = related_posts
        logger.info(f"🔗 Найдено связанных статей: {len(related_posts)}")
        
        # Получаем предыдущую и следующую статьи
        logger.info("⬅️➡️ Получаем соседние статьи")
        context['next_post'] = post.get_next_post()
        context['previous_post'] = post.get_previous_post()
        
        if context['next_post']:
            logger.info(f"➡️ Следующая статья: {context['next_post'].get_display_title()}")
        if context['previous_post']:
            logger.info(f"⬅️ Предыдущая статья: {context['previous_post'].get_display_title()}")
        
        # Получаем комментарии (только одобренные)
        logger.info("💬 Получаем комментарии")
        comments = post.comments.filter(is_approved=True).order_by('-created_at')
        context['comments'] = comments
        logger.info(f"💬 Найдено одобренных комментариев: {comments.count()}")
        
        logger.info("✅ Контекст для детальной страницы сформирован")
        return context


class CategoryView(ListView):
    """Статьи определенной категории с логированием"""
    model = BlogPost
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        """Получаем статьи категории"""
        category_slug = self.kwargs['slug']
        logger.info(f"📂 Получаем статьи для категории: '{category_slug}'")
        
        self.category = get_object_or_404(
            Category, 
            translations__slug=category_slug,
            is_active=True
        )
        
        category_name = self.category.safe_translation_getter('name', any_language=True)
        logger.info(f"📂 Категория найдена: '{category_name}' (ID={self.category.id})")
        
        queryset = BlogPost.objects.filter(
            category=self.category,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
        
        total_posts = queryset.count()
        logger.info(f"📄 Статей в категории: {total_posts}")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Формируем контекст для категории"""
        logger.info("🔧 Формируем контекст для CategoryView")
        
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        
        category_name = self.category.safe_translation_getter('name', any_language=True)
        context['page_title'] = f"{category_name} - Blog"
        context['page_description'] = (
            self.category.safe_translation_getter('description', any_language=True) or 
            f"Articles in {category_name} category"
        )
        
        logger.info(f"📂 Контекст категории: {category_name}")
        return context


class TagView(ListView):
    """Статьи с определенным тегом с логированием"""
    model = BlogPost
    template_name = 'blog/tag.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        """Получаем статьи по тегу"""
        self.tag_slug = self.kwargs['slug']
        logger.info(f"🏷️ Получаем статьи для тега: '{self.tag_slug}'")
        
        queryset = BlogPost.objects.filter(
            tags__slug=self.tag_slug,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
        
        total_posts = queryset.count()
        logger.info(f"📄 Статей с тегом '{self.tag_slug}': {total_posts}")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Формируем контекст для тега"""
        logger.info("🔧 Формируем контекст для TagView")
        
        context = super().get_context_data(**kwargs)
        context['tag_slug'] = self.tag_slug
        context['page_title'] = f"#{self.tag_slug} - Blog"
        context['page_description'] = f"Articles tagged with {self.tag_slug}"
        
        logger.info(f"🏷️ Контекст тега: {self.tag_slug}")
        return context


class SearchView(ListView):
    """Поиск по статьям с логированием"""
    model = BlogPost
    template_name = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        """Поиск статей"""
        query = self.request.GET.get('q', '')
        logger.info(f"🔍 Поиск по запросу: '{query}'")
        
        if query:
            queryset = BlogPost.objects.filter(
                translations__title__icontains=query,
                status='published'
            ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
            
            total_results = queryset.count()
            logger.info(f"🔍 Найдено результатов: {total_results}")
            
            return queryset
        else:
            logger.info("🔍 Пустой поисковый запрос")
            return BlogPost.objects.none()
    
    def get_context_data(self, **kwargs):
        """Формируем контекст для поиска"""
        logger.info("🔧 Формируем контекст для SearchView")
        
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        context['query'] = query
        context['page_title'] = f"Search results for '{query}'" if query else "Search"
        context['page_description'] = f"Search results for {query}" if query else "Search our blog"
        
        results_count = len(context.get('posts', []))
        logger.info(f"🔍 Результатов на странице: {results_count}")
        
        return context


# Дополнительные функции для отладки
def debug_media_files(request):
    """Отладочная view для проверки медиа файлов"""
    if not settings.DEBUG:
        raise Http404("Debug mode only")
    
    logger.info("🐛 Отладка медиа файлов")
    
    posts = BlogPost.objects.filter(status='published')
    
    debug_info = {
        'settings': {
            'MEDIA_URL': settings.MEDIA_URL,
            'MEDIA_ROOT': settings.MEDIA_ROOT,
            'DEBUG': settings.DEBUG,
        },
        'posts': [],
        'media_root_exists': os.path.exists(settings.MEDIA_ROOT),
        'media_root_writable': os.access(settings.MEDIA_ROOT, os.W_OK) if os.path.exists(settings.MEDIA_ROOT) else False,
    }
    
    for post in posts:
        post_info = {
            'id': post.id,
            'title': post.get_display_title(),
            'has_image': bool(post.featured_image),
        }
        
        if post.featured_image:
            post_info.update({
                'image_name': post.featured_image.name,
                'image_url': post.featured_image.url,
                'image_path': post.featured_image.path,
                'file_exists': os.path.exists(post.featured_image.path),
                'file_size': os.path.getsize(post.featured_image.path) if os.path.exists(post.featured_image.path) else None,
            })
        
        debug_info['posts'].append(post_info)
        logger.info(f"🐛 Пост {post.id}: изображение={bool(post.featured_image)}")
    
    from django.http import JsonResponse
    return JsonResponse(debug_info, indent=2)
