# backend/blog/admin.py - WORDPRESS СТИЛЬ АДМИНКИ - ЧАСТЬ 1 из 3
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from .models import BlogPost, Category, BlogImage, BlogComment
from filer.fields.image import FilerImageField
import json


class WordPressStyleAdminMixin:
    """Миксин для WordPress стиля - базовые методы"""
    
    def get_wordpress_badge(self, text, color='blue', icon=''):
        """Создает WordPress-стиль badge"""
        colors = {
            'blue': '#0073aa',
            'green': '#46b450', 
            'red': '#dc3232',
            'orange': '#f56e28',
            'gray': '#82878c',
            'yellow': '#ffb900'
        }
        return format_html(
            '<span class="wp-badge" style="background: {}; color: white; '
            'padding: 3px 8px; border-radius: 2px; font-size: 11px; '
            'font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; '
            'box-shadow: 0 1px 2px rgba(0,0,0,0.1);">'
            '{} {}</span>',
            colors.get(color, color), icon, text
        )
    
    def get_wordpress_button(self, text, url='#', style='primary', icon='', target=''):
        """Создает WordPress-стиль кнопку"""
        styles = {
            'primary': 'background: #0073aa; color: white; border: 1px solid #005177;',
            'secondary': 'background: #f1f1f1; color: #0073aa; border: 1px solid #0073aa;',
            'danger': 'background: #dc3232; color: white; border: 1px solid #c62d2d;',
            'success': 'background: #46b450; color: white; border: 1px solid #2e7d32;',
            'warning': 'background: #f56e28; color: white; border: 1px solid #e65100;'
        }
        target_attr = f'target="{target}"' if target else ''
        
        return format_html(
            '<a href="{}" {} class="wp-button" style="{} '
            'padding: 4px 10px; text-decoration: none; border-radius: 3px; '
            'font-size: 12px; font-weight: 600; display: inline-block; '
            'transition: all 0.2s ease; cursor: pointer; '
            'box-shadow: 0 1px 2px rgba(0,0,0,0.1);"'
            'onmouseover="this.style.transform=\'translateY(-1px)\'; this.style.boxShadow=\'0 2px 4px rgba(0,0,0,0.2)\';"'
            'onmouseout="this.style.transform=\'translateY(0)\'; this.style.boxShadow=\'0 1px 2px rgba(0,0,0,0.1)\';">'
            '{} {}</a>',
            url, target_attr, styles.get(style, styles['primary']), icon, text
        )
    
    def get_wordpress_stat_card(self, number, label, color='blue', icon='📊'):
        """Создает статистическую карточку"""
        colors = {
            'blue': '#0073aa',
            'green': '#46b450',
            'red': '#dc3232', 
            'orange': '#f56e28',
            'gray': '#82878c'
        }
        return format_html(
            '<div class="wp-stat-card" style="text-align: center; padding: 15px; '
            'background: white; border-radius: 4px; border-left: 4px solid {}; '
            'box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-width: 120px;">'
            '<div style="font-size: 24px; font-weight: bold; color: {}; margin-bottom: 5px;">{}</div>'
            '<div style="font-size: 12px; color: #666; text-transform: uppercase; '
            'letter-spacing: 0.5px;">{} {}</div>'
            '</div>',
            colors.get(color, color), colors.get(color, color), number, icon, label
        )


class BlogImageInline(admin.TabularInline, WordPressStyleAdminMixin):
    """WordPress-стиль inline для изображений"""
    model = BlogImage
    extra = 1
    fields = ('image_thumbnail', 'image', 'alt_text', 'caption', 'image_actions')
    readonly_fields = ('image_thumbnail', 'image_actions')
    classes = ['wp-inline']
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<div class="wp-media-thumbnail" style="position: relative;">'
                '<img src="{}" style="width: 80px; height: 60px; '
                'object-fit: cover; border-radius: 4px; border: 2px solid #ddd; '
                'transition: all 0.2s ease;" '
                'onmouseover="this.style.borderColor=\'#0073aa\'; this.style.transform=\'scale(1.05)\';"'
                'onmouseout="this.style.borderColor=\'#ddd\'; this.style.transform=\'scale(1)\';" />'
                '<div style="position: absolute; top: 2px; right: 2px; '
                'background: rgba(0,0,0,0.7); color: white; border-radius: 2px; '
                'padding: 1px 4px; font-size: 9px;">📷</div>'
                '</div>',
                obj.image.url
            )
        return format_html(
            '<div class="wp-media-placeholder" style="width: 80px; height: 60px; '
            'background: linear-gradient(135deg, #f1f1f1, #e1e1e1); '
            'border-radius: 4px; display: flex; align-items: center; '
            'justify-content: center; border: 2px dashed #ddd; color: #666;">'
            '<span style="font-size: 24px;">📷</span>'
            '</div>'
        )
    image_thumbnail.short_description = 'Preview'
    
    def image_actions(self, obj):
        if obj.pk:
            return format_html(
                '<div class="wp-media-actions" style="display: flex; gap: 4px;">'
                '{} {}'
                '</div>',
                self.get_wordpress_button('Edit', f'/admin/blog/blogimage/{obj.pk}/change/', 'secondary', '✏️'),
                self.get_wordpress_button('Del', f'/admin/blog/blogimage/{obj.pk}/delete/', 'danger', '🗑️')
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    image_actions.short_description = 'Actions'
    
    class Media:
        css = {'all': ('/static/admin/css/custom_admin.css',)}


class BlogCommentInline(admin.TabularInline, WordPressStyleAdminMixin):
    """WordPress-стиль inline для комментариев"""
    model = BlogComment
    extra = 0
    fields = ('author_avatar', 'name', 'content_preview', 'approval_badge', 'comment_actions', 'created_at')
    readonly_fields = ('author_avatar', 'content_preview', 'approval_badge', 'comment_actions', 'created_at')
    classes = ['wp-inline', 'wp-comments']
    
    def author_avatar(self, obj):
        # Генерируем аватар по первой букве имени
        initial = obj.name[0].upper() if obj.name else '?'
        colors = ['#0073aa', '#46b450', '#dc3232', '#f56e28', '#82878c', '#ffb900']
        color = colors[hash(obj.name) % len(colors)] if obj.name else '#82878c'
        
        return format_html(
            '<div class="wp-avatar" style="width: 40px; height: 40px; '
            'background: linear-gradient(135deg, {}, {}); color: white; '
            'border-radius: 50%; display: flex; align-items: center; '
            'justify-content: center; font-weight: bold; font-size: 16px; '
            'border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2); '
            'transition: all 0.2s ease;" '
            'onmouseover="this.style.transform=\'scale(1.1)\';"'
            'onmouseout="this.style.transform=\'scale(1)\';">{}</div>',
            color, color + '80', initial
        )
    author_avatar.short_description = ''
    
    def content_preview(self, obj):
        preview = obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
        word_count = len(obj.content.split())
        
        return format_html(
            '<div class="wp-comment-preview" style="max-width: 300px;">'
            '<div style="background: #f9f9f9; padding: 8px; border-radius: 4px; '
            'border-left: 3px solid #0073aa; font-style: italic; line-height: 1.4; '
            'color: #444; margin-bottom: 4px; font-size: 12px;">{}</div>'
            '<div style="font-size: 10px; color: #999;">{} words • {}</div>'
            '</div>',
            preview, word_count, obj.created_at.strftime('%b %d')
        )
    content_preview.short_description = 'Comment'
    
    def approval_badge(self, obj):
        if obj.is_approved:
            return self.get_wordpress_badge('Live', 'green', '✓')
        return self.get_wordpress_badge('Pending', 'orange', '⏳')
    approval_badge.short_description = 'Status'
    
    def comment_actions(self, obj):
        if obj.pk:
            approve_btn = '' if obj.is_approved else self.get_wordpress_button(
                'OK', f'/admin/blog/blogcomment/{obj.pk}/approve/', 'success', '✓'
            )
            return format_html(
                '<div class="wp-comment-actions" style="display: flex; gap: 2px; flex-direction: column;">'
                '{} {}'
                '</div>',
                approve_btn,
                self.get_wordpress_button('Edit', f'/admin/blog/blogcomment/{obj.pk}/change/', 'secondary', '✏️')
            )
        return '-'
    comment_actions.short_description = 'Actions'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin, WordPressStyleAdminMixin):
    """WordPress-стиль админка для категорий"""
    list_display = (
        'category_icon', 'get_name_styled', 'get_slug_styled', 
        'post_statistics', 'status_toggle', 'category_actions'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('translations__name', 'translations__description')
    list_per_page = 20
    
    # WordPress-стиль fieldsets
    fieldsets = (
        ('📁 Category Information', {
            'fields': ('name', 'slug', 'description'),
            'classes': ('wp-box', 'wp-box-primary'),
            'description': 'Basic category details and URL slug configuration'
        }),
        ('⚙️ Publishing Options', {
            'fields': ('is_active',),
            'classes': ('wp-box', 'wp-box-secondary'),
            'description': 'Control category visibility on your website'
        }),
        ('📊 Statistics', {
            'fields': ('category_stats_display',),
            'classes': ('wp-box', 'wp-box-analytics'),
            'description': 'Category performance and usage statistics'
        }),
    )
    
    readonly_fields = ('category_stats_display',)
    
    def category_icon(self, obj):
        return format_html(
            '<div class="wp-category-icon" style="font-size: 24px; text-align: center; '
            'background: linear-gradient(135deg, #0073aa, #00a0d2); '
            'color: white; width: 40px; height: 40px; border-radius: 8px; '
            'display: flex; align-items: center; justify-content: center; '
            'box-shadow: 0 2px 4px rgba(0,0,0,0.1);">📁</div>'
        )
    category_icon.short_description = ''
    
    def get_name_styled(self, obj):
        name = obj.safe_translation_getter('name', any_language=True) or f'Category {obj.pk}'
        post_count = obj.posts.count()
        
        return format_html(
            '<div class="wp-category-name" style="display: flex; flex-direction: column;">'
            '<div style="font-weight: bold; color: #0073aa; font-size: 14px; '
            'margin-bottom: 2px;">{}</div>'
            '<div style="font-size: 11px; color: #666;">{} post{}</div>'
            '</div>',
            name, post_count, 's' if post_count != 1 else ''
        )
    get_name_styled.short_description = 'Category'
    get_name_styled.admin_order_field = 'translations__name'
    
    def get_slug_styled(self, obj):
        slug = obj.safe_translation_getter('slug', any_language=True)
        if slug:
            return format_html(
                '<div style="font-family: monospace; background: #f1f1f1; '
                'padding: 4px 8px; border-radius: 3px; font-size: 11px; '
                'color: #666; border: 1px solid #ddd; display: inline-block;">'
                '<span style="color: #999;">../</span>{}'
                '</div>',
                slug
            )
        return format_html(
            '<span style="color: #dc3232; font-style: italic; font-size: 11px;">⚠️ No slug</span>'
        )
    get_slug_styled.short_description = 'URL Slug'
    get_slug_styled.admin_order_field = 'translations__slug'
    
    def post_statistics(self, obj):
        published = obj.posts.filter(status='published').count()
        draft = obj.posts.filter(status='draft').count()
        total = obj.posts.count()
        
        # Определяем цвет по активности
        if published > 5:
            main_color, performance = '#46b450', 'High'
        elif published > 0:
            main_color, performance = '#f56e28', 'Medium'
        else:
            main_color, performance = '#82878c', 'Low'
        
        return format_html(
            '<div class="wp-post-stats" style="text-align: center; '
            'background: linear-gradient(135deg, #f9f9f9, #f1f1f1); '
            'padding: 8px; border-radius: 6px; border: 1px solid #e1e1e1;">'
            '<div style="display: flex; justify-content: center; gap: 10px; margin-bottom: 4px;">'
            '<div style="text-align: center;">'
            '<div style="font-size: 16px; font-weight: bold; color: {};">{}</div>'
            '<div style="font-size: 9px; color: #666;">PUBLISHED</div>'
            '</div>'
            '<div style="text-align: center;">'
            '<div style="font-size: 14px; font-weight: bold; color: #82878c;">{}</div>'
            '<div style="font-size: 9px; color: #666;">DRAFT</div>'
            '</div>'
            '</div>'
            '<div style="font-size: 9px; color: {}; font-weight: bold; '
            'text-transform: uppercase;">{} Activity</div>'
            '</div>',
            main_color, published, draft, main_color, performance
        )
    post_statistics.short_description = 'Posts'
    
    def status_toggle(self, obj):
        if obj.is_active:
            return format_html(
                '<div style="text-align: center;">'
                '{}'
                '<div style="font-size: 10px; color: #46b450; margin-top: 3px; '
                'font-weight: bold;">VISIBLE</div>'
                '</div>',
                self.get_wordpress_badge('Active', 'green', '✓')
            )
        return format_html(
            '<div style="text-align: center;">'
            '{}'
            '<div style="font-size: 10px; color: #82878c; margin-top: 3px; '
            'font-weight: bold;">HIDDEN</div>'
            '</div>',
            self.get_wordpress_badge('Inactive', 'gray', '○')
        )
    status_toggle.short_description = 'Status'
    status_toggle.admin_order_field = 'is_active'
    
    def category_actions(self, obj):
        if obj.pk:
            return format_html(
                '<div class="wp-actions" style="display: flex; flex-direction: column; gap: 4px;">'
                '{}'
                '{}'
                '{}'
                '</div>',
                self.get_wordpress_button('Edit', f'/admin/blog/category/{obj.pk}/change/', 'primary', '✏️'),
                self.get_wordpress_button('Posts', f'/admin/blog/blogpost/?category__id__exact={obj.pk}', 'secondary', '📝'),
                self.get_wordpress_button('View', f'/blog/category/{obj.safe_translation_getter("slug", any_language=True)}/', 'secondary', '👁️', '_blank') if obj.safe_translation_getter('slug', any_language=True) else ''
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    category_actions.short_description = 'Actions'
    
    def category_stats_display(self, obj):
        """Подробная статистика категории"""
        if not obj.pk:
            return format_html('<p style="color: #999;">Save category to see statistics</p>')
        
        total_posts = obj.posts.count()
        published_posts = obj.posts.filter(status='published').count()
        draft_posts = obj.posts.filter(status='draft').count()
        featured_posts = obj.posts.filter(is_featured=True).count()
        total_views = sum(post.views_count for post in obj.posts.all())
        
        return format_html(
            '<div class="wp-category-stats" style="background: #f9f9f9; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 15px 0; color: #0073aa;">📊 Category Analytics</h4>'
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px;">'
            '{}'
            '{}'
            '{}'
            '{}'
            '{}'
            '</div>'
            '</div>',
            self.get_wordpress_stat_card(total_posts, 'Total Posts', 'blue', '📝'),
            self.get_wordpress_stat_card(published_posts, 'Published', 'green', '✓'),
            self.get_wordpress_stat_card(draft_posts, 'Drafts', 'gray', '📋'),
            self.get_wordpress_stat_card(featured_posts, 'Featured', 'orange', '⭐'),
            self.get_wordpress_stat_card(total_views, 'Total Views', 'blue', '👁️')
        )
    category_stats_display.short_description = 'Detailed Statistics'
    
    # WordPress-стиль действия
    actions = ['activate_categories', 'deactivate_categories', 'export_categories']
    
    def activate_categories(self, request, queryset):
        count = queryset.update(is_active=True)
        messages.success(request, f'✅ {count} categor{"ies" if count != 1 else "y"} activated!')
    activate_categories.short_description = "✅ Activate selected categories"
    
    def deactivate_categories(self, request, queryset):
        count = queryset.update(is_active=False)
        messages.warning(request, f'⏸️ {count} categor{"ies" if count != 1 else "y"} deactivated.')
    deactivate_categories.short_description = "⏸️ Deactivate selected categories"
    
    def export_categories(self, request, queryset):
        categories_data = []
        for category in queryset:
            categories_data.append({
                'name': category.safe_translation_getter('name', any_language=True),
                'slug': category.safe_translation_getter('slug', any_language=True),
                'description': category.safe_translation_getter('description', any_language=True),
                'is_active': category.is_active,
                'post_count': category.posts.count(),
                'published_posts': category.posts.filter(status='published').count(),
                'created_at': category.created_at.isoformat(),
            })
        
        response = HttpResponse(
            json.dumps(categories_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="blog_categories_export.json"'
        return response
    export_categories.short_description = "📥 Export selected categories"
    
    class Media:
        css = {'all': ('/static/admin/css/custom_admin.css',)}
        js = ('/static/admin/js/custom_admin.js',)

# Конец Части 1 - продолжение в Части 2
# ЧАСТЬ 2 из 3 - BlogPost Admin (продолжение admin.py)

@admin.register(BlogPost)
class BlogPostAdmin(TranslatableAdmin, WordPressStyleAdminMixin):
    """WordPress-стиль админка для постов - главная жемчужина"""
    
    list_display = (
        'post_thumbnail', 'get_title_with_status', 'author_info', 
        'category_info', 'post_stats', 'seo_score', 'post_actions'
    )
    list_filter = (
        'status', 'is_featured', 'category', 'created_at', 
        'published_at', 'allow_comments', 'translations__schema_article_type'
    )
    search_fields = (
        'translations__title', 'translations__content', 
        'author__username', 'author__first_name', 'author__last_name'
    )
    readonly_fields = (
        'post_preview_card', 'seo_preview_card', 'social_preview_card',
        'post_analytics_dashboard', 'views_count', 'created_at', 'updated_at'
    )
    filter_horizontal = ('tags',)
    list_per_page = 20
    date_hierarchy = 'published_at'
    
    # WordPress-стиль группировка полей (как в реальном WP)
    fieldsets = (
        ('✏️ Post Content', {
            'fields': ('title', 'slug', 'content', 'excerpt'),
            'classes': ('wp-box', 'wp-box-primary'),
            'description': 'Write your amazing content here. The title and content are the heart of your post.'
        }),
        ('📅 Publishing Settings', {
            'fields': ('status', 'published_at', 'author', 'category', 'tags'),
            'classes': ('wp-box', 'wp-box-secondary'),
            'description': 'Control when and how your post appears to your audience'
        }),
        ('🖼️ Featured Image', {
            'fields': ('featured_image', 'post_preview_card'),
            'classes': ('wp-box', 'wp-box-media'),
            'description': 'Add a stunning featured image (recommended: 1200x630px for social media)'
        }),
        ('⚙️ Post Options', {
            'fields': ('is_featured', 'allow_comments', 'reading_time'),
            'classes': ('wp-box', 'wp-box-options'),
            'description': 'Additional settings for your post behavior'
        }),
        ('🔍 SEO Optimization', {
            'fields': (
                'seo_preview_card',
                'meta_title', 'meta_description', 'meta_keywords',
                'og_title', 'og_description', 'schema_article_type'
            ),
            'classes': ('wp-box', 'wp-box-seo', 'collapse'),
            'description': 'Optimize your post for search engines and social media sharing'
        }),
        ('📱 Social Media Preview', {
            'fields': ('social_preview_card',),
            'classes': ('wp-box', 'wp-box-social', 'collapse'),
            'description': 'See how your post will look when shared on social platforms'
        }),
        ('📊 Analytics & Performance', {
            'fields': ('post_analytics_dashboard', 'views_count', 'created_at', 'updated_at'),
            'classes': ('wp-box', 'wp-box-analytics', 'collapse'),
            'description': 'Track your post performance and engagement metrics'
        }),
    )
    
    inlines = [BlogImageInline, BlogCommentInline]
    
    # WordPress-стиль массовые действия
    actions = [
        'publish_posts', 'draft_posts', 'feature_posts', 
        'unfeature_posts', 'reset_stats', 'duplicate_posts',
        'export_posts', 'seo_audit', 'generate_social_images'
    ]
    
    def post_thumbnail(self, obj):
        """Thumbnail как в WordPress медиа-библиотеке"""
        if obj.featured_image:
            return format_html(
                '<div class="wp-post-thumbnail" style="position: relative; '
                'border-radius: 6px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">'
                '<img src="{}" style="width: 70px; height: 52px; '
                'object-fit: cover; transition: all 0.3s ease;" '
                'onmouseover="this.style.transform=\'scale(1.1)\';"'
                'onmouseout="this.style.transform=\'scale(1)\';" />'
                '<div style="position: absolute; top: 4px; right: 4px; '
                'background: rgba(0,115,170,0.9); color: white; border-radius: 2px; '
                'padding: 1px 4px; font-size: 9px; font-weight: bold;">IMG</div>'
                '{}'
                '</div>',
                obj.featured_image.url,
                '<div style="position: absolute; bottom: 2px; left: 2px; right: 2px; '
                'background: linear-gradient(transparent, rgba(0,0,0,0.7)); '
                'color: white; font-size: 8px; padding: 2px; text-align: center; '
                'border-radius: 0 0 4px 4px;">Featured</div>' if obj.is_featured else ''
            )
        return format_html(
            '<div class="wp-post-thumbnail-placeholder" style="width: 70px; height: 52px; '
            'background: linear-gradient(135deg, #f1f1f1, #e1e1e1); '
            'border-radius: 6px; display: flex; align-items: center; '
            'justify-content: center; border: 2px dashed #ddd; position: relative;">'
            '<span style="font-size: 20px; color: #999;">📷</span>'
            '<div style="position: absolute; bottom: 1px; left: 2px; right: 2px; '
            'font-size: 7px; color: #999; text-align: center;">No Image</div>'
            '</div>'
        )
    post_thumbnail.short_description = ''
    
    def get_title_with_status(self, obj):
        """Заголовок со статусом как в WordPress"""
        title = obj.safe_translation_getter('title', any_language=True) or f"Post {obj.pk}"
        
        # WordPress-стиль иконки статусов
        status_config = {
            'published': {'icon': '✓', 'color': '#46b450', 'label': 'Published'},
            'draft': {'icon': '📝', 'color': '#82878c', 'label': 'Draft'}, 
            'scheduled': {'icon': '⏰', 'color': '#0073aa', 'label': 'Scheduled'}
        }
        
        config = status_config.get(obj.status, status_config['draft'])
        
        # Обрезаем длинные заголовки
        display_title = title[:50] + '...' if len(title) > 50 else title
        
        # Добавляем индикатор комментариев
        comment_count = obj.comments.filter(is_approved=True).count()
        comment_indicator = f' <span style="color: #82878c;">({comment_count} 💬)</span>' if comment_count > 0 else ''
        
        return format_html(
            '<div class="wp-post-title" style="display: flex; flex-direction: column; gap: 3px;">'
            '<div style="font-weight: bold; color: #23282d; font-size: 14px; line-height: 1.3;" title="{}">'
            '{}{}'
            '</div>'
            '<div style="display: flex; align-items: center; gap: 6px;">'
            '{}'
            '{}'
            '{}'
            '</div>'
            '</div>',
            title,  # полный заголовок для tooltip
            display_title,
            comment_indicator,
            self.get_wordpress_badge(config['label'], config['color'].replace('#', ''), config['icon']),
            '<span style="font-size: 10px; color: #f56e28; font-weight: bold;">🌟 FEATURED</span>' if obj.is_featured else '',
            f'<span style="font-size: 10px; color: #0073aa;">📅 {obj.published_at.strftime("%b %d")}</span>' if obj.published_at else ''
        )
    get_title_with_status.short_description = 'Post'
    get_title_with_status.admin_order_field = 'translations__title'
    
    def author_info(self, obj):
        """Информация об авторе как в WordPress"""
        if obj.author:
            full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
            display_name = full_name if full_name else obj.author.username
            
            # Аватар автора (первая буква)
            initial = display_name[0].upper()
            colors = ['#0073aa', '#46b450', '#dc3232', '#f56e28', '#82878c']
            color = colors[hash(obj.author.username) % len(colors)]
            
            return format_html(
                '<div class="wp-author-info" style="display: flex; align-items: center; gap: 8px;">'
                '<div style="width: 32px; height: 32px; background: {}; color: white; '
                'border-radius: 50%; display: flex; align-items: center; justify-content: center; '
                'font-weight: bold; font-size: 14px; border: 2px solid white; '
                'box-shadow: 0 1px 3px rgba(0,0,0,0.2);">{}</div>'
                '<div style="display: flex; flex-direction: column;">'
                '<div style="font-weight: bold; color: #0073aa; font-size: 12px;">{}</div>'
                '<div style="font-size: 10px; color: #666;">@{}</div>'
                '</div>'
                '</div>',
                color, initial, display_name, obj.author.username
            )
        return format_html('<span style="color: #dc3232; font-style: italic;">No author</span>')
    author_info.short_description = 'Author'
    author_info.admin_order_field = 'author__username'
    
    def category_info(self, obj):
        """Информация о категории как в WordPress"""
        if obj.category:
            category_name = obj.category.safe_translation_getter('name', any_language=True) or 'Unnamed'
            post_count = obj.category.posts.filter(status='published').count()
            
            # Определяем цвет по количеству постов
            if post_count > 10:
                color, intensity = '#46b450', 'High'
            elif post_count > 3:
                color, intensity = '#f56e28', 'Medium'
            else:
                color, intensity = '#82878c', 'Low'
            
            return format_html(
                '<div class="wp-category-info" style="text-align: center;">'
                '<div style="background: {}; color: white; padding: 4px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold; '
                'margin-bottom: 3px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">📁 {}</div>'
                '<div style="font-size: 9px; color: #666;">{} posts • {} activity</div>'
                '</div>',
                color, category_name, post_count, intensity
            )
        return format_html(
            '<div style="text-align: center; color: #dc3232; font-style: italic; font-size: 11px;">'
            '⚠️ Uncategorized</div>'
        )
    category_info.short_description = 'Category'
    category_info.admin_order_field = 'category__translations__name'
    
    def post_stats(self, obj):
        """Статистика поста как в WordPress Analytics"""
        views = obj.views_count
        comments = obj.comments.filter(is_approved=True).count()
        images = obj.images.count()
        
        # Определяем "популярность"
        if views > 1000:
            popularity_color, popularity_text = '#46b450', 'Hot'
        elif views > 100:
            popularity_color, popularity_text = '#f56e28', 'Warm'
        else:
            popularity_color, popularity_text = '#82878c', 'Cool'
        
        return format_html(
            '<div class="wp-post-stats" style="background: linear-gradient(135deg, #f9f9f9, #f1f1f1); '
            'padding: 8px; border-radius: 6px; border: 1px solid #e1e1e1; text-align: center;">'
            '<div style="display: flex; justify-content: center; gap: 8px; margin-bottom: 4px;">'
            '<div style="text-align: center;">'
            '<div style="font-size: 14px; font-weight: bold; color: {};">{}</div>'
            '<div style="font-size: 8px; color: #666;">VIEWS</div>'
            '</div>'
            '<div style="text-align: center;">'
            '<div style="font-size: 12px; font-weight: bold; color: #0073aa;">{}</div>'
            '<div style="font-size: 8px; color: #666;">COMMENTS</div>'
            '</div>'
            '<div style="text-align: center;">'
            '<div style="font-size: 12px; font-weight: bold; color: #82878c;">{}</div>'
            '<div style="font-size: 8px; color: #666;">IMAGES</div>'
            '</div>'
            '</div>'
            '<div style="font-size: 8px; color: {}; font-weight: bold; '
            'text-transform: uppercase;">📈 {}</div>'
            '</div>',
            popularity_color, views, comments, images, popularity_color, popularity_text
        )
    post_stats.short_description = 'Stats'
    
    def seo_score(self, obj):
        """SEO Score как в Yoast WordPress"""
        score = 0
        issues = []
        
        # Проверяем SEO элементы
        title = obj.safe_translation_getter('meta_title', any_language=True) or obj.safe_translation_getter('title', any_language=True)
        description = obj.safe_translation_getter('meta_description', any_language=True)
        
        if title:
            if 30 <= len(title) <= 60:
                score += 25
            else:
                issues.append('Title length')
        else:
            issues.append('No title')
            
        if description:
            if 120 <= len(description) <= 160:
                score += 25
            else:
                issues.append('Description length')
        else:
            issues.append('No description')
            
        if obj.featured_image:
            score += 20
        else:
            issues.append('No featured image')
            
        if obj.safe_translation_getter('meta_keywords', any_language=True):
            score += 15
        else:
            issues.append('No keywords')
            
        if obj.safe_translation_getter('slug', any_language=True):
            score += 15
        else:
            issues.append('No slug')
        
        # Определяем цвет и статус
        if score >= 80:
            color, status, icon = '#46b450', 'Excellent', '🟢'
        elif score >= 60:
            color, status, icon = '#f56e28', 'Good', '🟡'
        elif score >= 40:
            color, status, icon = '#ff8c00', 'Needs Work', '🟠'
        else:
            color, status, icon = '#dc3232', 'Poor', '🔴'
        
        return format_html(
            '<div class="wp-seo-score" style="text-align: center; '
            'background: linear-gradient(135deg, #fff, #f9f9f9); '
            'padding: 10px; border-radius: 6px; border: 1px solid #e1e1e1;">'
            '<div style="font-size: 20px; font-weight: bold; color: {}; margin-bottom: 4px;">'
            '{} {}%</div>'
            '<div style="font-size: 10px; color: {}; font-weight: bold; '
            'text-transform: uppercase; margin-bottom: 3px;">{}</div>'
            '<div style="font-size: 8px; color: #666;" title="{}">'
            '{} issue{}</div>'
            '</div>',
            color, icon, score, color, status, 
            ', '.join(issues) if issues else 'All good!',
            len(issues), 's' if len(issues) != 1 else ''
        )
    seo_score.short_description = 'SEO'
    
    def post_actions(self, obj):
        """Действия для поста как в WordPress"""
        if obj.pk:
            actions = []
            
            # Edit button
            actions.append(
                self.get_wordpress_button('Edit', f'/admin/blog/blogpost/{obj.pk}/change/', 'primary', '✏️')
            )
            
            # View button (если пост опубликован)
            if obj.status == 'published':
                try:
                    slug = obj.safe_translation_getter('slug', any_language=True)
                    if slug:
                        actions.append(
                            self.get_wordpress_button('View', f'/blog/{slug}/', 'secondary', '👁️', '_blank')
                        )
                except:
                    pass
            
            # Quick publish/unpublish
            if obj.status != 'published':
                actions.append(
                    self.get_wordpress_button('Publish', f'/admin/blog/blogpost/{obj.pk}/quick-publish/', 'success', '🚀')
                )
            else:
                actions.append(
                    self.get_wordpress_button('Draft', f'/admin/blog/blogpost/{obj.pk}/quick-draft/', 'warning', '📝')
                )
            
            # Duplicate button
            actions.append(
                self.get_wordpress_button('Copy', f'/admin/blog/blogpost/{obj.pk}/duplicate/', 'secondary', '📄')
            )
            
            return format_html(
                '<div class="wp-post-actions" style="display: flex; flex-direction: column; gap: 3px;">'
                '{}'
                '</div>',
                ''.join(actions)
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    post_actions.short_description = 'Actions'
    
    # WordPress-стиль readonly поля для детальной информации
    def post_preview_card(self, obj):
        """Карточка предпросмотра поста"""
        if not obj.pk:
            return format_html('<p style="color: #999;">Save post to see preview</p>')
        
        title = obj.safe_translation_getter('title', any_language=True) or 'No title'
        excerpt = obj.safe_translation_getter('excerpt', any_language=True) or 'No excerpt'
        
        return format_html(
            '<div class="wp-post-preview" style="background: white; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
            '<div style="display: flex; gap: 15px;">'
            '{}'
            '<div style="flex: 1;">'
            '<h3 style="margin: 0 0 10px 0; color: #0073aa; font-size: 18px; line-height: 1.3;">{}</h3>'
            '<p style="color: #666; font-size: 14px; line-height: 1.5; margin: 0;">{}</p>'
            '<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #f1f1f1; '
            'display: flex; gap: 10px; font-size: 12px; color: #999;">'
            '<span>👤 {}</span>'
            '<span>📁 {}</span>'
            '<span>📅 {}</span>'
            '</div>'
            '</div>'
            '</div>'
            '</div>',
            f'<img src="{obj.featured_image.url}" style="width: 150px; height: 100px; '
            f'object-fit: cover; border-radius: 4px;" />' if obj.featured_image else 
            '<div style="width: 150px; height: 100px; background: #f1f1f1; '
            'border-radius: 4px; display: flex; align-items: center; justify-content: center; '
            'color: #999; font-size: 24px;">📷</div>',
            title,
            excerpt[:150] + '...' if len(excerpt) > 150 else excerpt,
            obj.author.username if obj.author else 'No author',
            obj.category.safe_translation_getter('name', any_language=True) if obj.category else 'Uncategorized',
            obj.published_at.strftime('%B %d, %Y') if obj.published_at else 'Not published'
        )
    post_preview_card.short_description = 'Post Preview'
    
    def seo_preview_card(self, obj):
        """SEO предпросмотр как в Yoast"""
        title = obj.safe_translation_getter('meta_title', any_language=True) or obj.safe_translation_getter('title', any_language=True) or 'No title'
        description = obj.safe_translation_getter('meta_description', any_language=True) or 'No meta description'
        
        try:
            slug = obj.safe_translation_getter('slug', any_language=True)
            url = f"yoursite.com/blog/{slug}/" if slug else "yoursite.com/blog/post-url/"
        except:
            url = "yoursite.com/blog/post-url/"
        
        return format_html(
            '<div class="wp-seo-preview" style="background: white; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 15px 0; color: #0073aa;">🔍 Google Search Preview</h4>'
            '<div style="border: 1px solid #ddd; padding: 15px; border-radius: 4px; background: #fafafa;">'
            '<div style="color: #1a0dab; font-size: 18px; margin-bottom: 5px; cursor: pointer; '
            'text-decoration: underline;">{}</div>'
            '<div style="color: #006621; font-size: 14px; margin-bottom: 8px;">{}</div>'
            '<div style="color: #545454; font-size: 13px; line-height: 1.4;">{}</div>'
            '</div>'
            '<div style="margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 15px; '
            'font-size: 12px;">'
            '<div><strong>Title length:</strong> {} chars {}</div>'
            '<div><strong>Description length:</strong> {} chars {}</div>'
            '</div>'
            '</div>',
            title,
            url,
            description,
            len(title),
            '✅' if 30 <= len(title) <= 60 else '⚠️',
            len(description),
            '✅' if 120 <= len(description) <= 160 else '⚠️'
        )
    seo_preview_card.short_description = 'SEO Preview'
    
    def social_preview_card(self, obj):
        """Предпросмотр для соцсетей"""
        og_title = obj.safe_translation_getter('og_title', any_language=True) or obj.safe_translation_getter('title', any_language=True) or 'No title'
        og_description = obj.safe_translation_getter('og_description', any_language=True) or obj.safe_translation_getter('meta_description', any_language=True) or 'No description'
        
        return format_html(
            '<div class="wp-social-preview" style="background: white; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 15px 0; color: #0073aa;">📱 Social Media Preview</h4>'
            '<div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; '
            'background: white; max-width: 500px;">'
            '{}'
            '<div style="padding: 15px;">'
            '<div style="color: #999; font-size: 12px; text-transform: uppercase; '
            'margin-bottom: 5px;">YOURSITE.COM</div>'
            '<div style="font-weight: bold; color: #1d2129; font-size: 16px; '
            'margin-bottom: 5px; line-height: 1.3;">{}</div>'
            '<div style="color: #606770; font-size: 14px; line-height: 1.4;">{}</div>'
            '</div>'
            '</div>'
            '</div>',
            f'<img src="{obj.featured_image.url}" style="width: 100%; height: 250px; '
            f'object-fit: cover;" />' if obj.featured_image else 
            '<div style="width: 100%; height: 250px; background: linear-gradient(135deg, #f1f1f1, #e1e1e1); '
            'display: flex; align-items: center; justify-content: center; color: #999; font-size: 48px;">📷</div>',
            og_title[:70] + '...' if len(og_title) > 70 else og_title,
            og_description[:120] + '...' if len(og_description) > 120 else og_description
        )
    social_preview_card.short_description = 'Social Preview'
    
    def post_analytics_dashboard(self, obj):
        """Аналитическая панель как в WordPress"""
        if not obj.pk:
            return format_html('<p style="color: #999;">Save post to see analytics</p>')
        
        # Собираем статистику
        total_views = obj.views_count
        total_comments = obj.comments.count()
        approved_comments = obj.comments.filter(is_approved=True).count()
        pending_comments = total_comments - approved_comments
        total_images = obj.images.count()
        
        # Примерные данные для демонстрации
        reading_time = obj.reading_time or 5
        
        # Определяем общую оценку поста
        if total_views > 500 and approved_comments > 10:
            performance_color, performance_text = '#46b450', 'Excellent'
        elif total_views > 100 and approved_comments > 3:
            performance_color, performance_text = '#f56e28', 'Good'
        else:
            performance_color, performance_text = '#82878c', 'Needs promotion'
        
        return format_html(
            '<div class="wp-analytics-dashboard" style="background: #f9f9f9; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 20px 0; color: #0073aa;">📊 Post Analytics Dashboard</h4>'
            
            # Основные метрики
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); '
            'gap: 15px; margin-bottom: 20px;">'
            '{}'
            '{}'
            '{}'
            '{}'
            '{}'
            '</div>'
            
            # Общая оценка
            '<div style="background: white; padding: 15px; border-radius: 6px; '
            'border-left: 4px solid {}; text-align: center;">'
            '<div style="font-size: 16px; font-weight: bold; color: {}; margin-bottom: 5px;">'
            '🏆 Overall Performance: {}</div>'
            '<div style="font-size: 12px; color: #666;">Based on views, engagement and content quality</div>'
            '</div>'
            '</div>',
            self.get_wordpress_stat_card(total_views, 'Page Views', 'blue', '👁️'),
            self.get_wordpress_stat_card(approved_comments, 'Comments', 'green', '💬'),
            self.get_wordpress_stat_card(pending_comments, 'Pending', 'orange', '⏳'),
            self.get_wordpress_stat_card(total_images, 'Images', 'gray', '📷'),
            self.get_wordpress_stat_card(f'{reading_time}m', 'Read Time', 'blue', '⏰'),
            performance_color, performance_color, performance_text
        )
    post_analytics_dashboard.short_description = 'Analytics Dashboard'
    
    # WordPress-стиль действия
    def publish_posts(self, request, queryset):
        count = queryset.update(status='published', published_at=timezone.now())
        messages.success(request, f'🚀 {count} post{"s" if count != 1 else ""} published successfully!')
    publish_posts.short_description = "🚀 Publish selected posts"
    
    def draft_posts(self, request, queryset):
        count = queryset.update(status='draft')
        messages.warning(request, f'📝 {count} post{"s" if count != 1 else ""} moved to draft.')
    draft_posts.short_description = "📝 Move to draft"
    
    def feature_posts(self, request, queryset):
        count = queryset.update(is_featured=True)
        messages.success(request, f'⭐ {count} post{"s" if count != 1 else ""} marked as featured!')
    feature_posts.short_description = "⭐ Mark as featured"
    
    def unfeature_posts(self, request, queryset):
        count = queryset.update(is_featured=False)
        messages.info(request, f'🔄 {count} post{"s" if count != 1 else ""} removed from featured.')
    unfeature_posts.short_description = "🔄 Remove from featured"
    
    def reset_stats(self, request, queryset):
        count = queryset.update(views_count=0)
        messages.warning(request, f'🔄 {count} post{"s" if count != 1 else ""} view counts reset to 0.')
    reset_stats.short_description = "🔄 Reset view counts"
    
    @staff_member_required
    def duplicate_posts(self, request, queryset):
        """Дублирование постов как в WordPress"""
        duplicated_count = 0
        for post in queryset:
            # Создаем копию поста
            original_title = post.safe_translation_getter('title', any_language=True) or f'Post {post.pk}'
            
            # Дублируем основной объект
            post.pk = None
            post.slug = None  # Будет сгенерирован автоматически
            post.status = 'draft'
            post.published_at = None
            post.views_count = 0
            post.save()
            
            # Обновляем переводы
            for translation in post.translations.all():
                translation.pk = None
                translation.master = post
                translation.title = f'Copy of {translation.title}' if translation.title else f'Copy of {original_title}'
                translation.slug = None  # Будет сгенерирован
                translation.save()
            
            duplicated_count += 1
        
        messages.success(request, f'📄 {duplicated_count} post{"s" if duplicated_count != 1 else ""} duplicated successfully!')
    duplicate_posts.short_description = "📄 Duplicate selected posts"
    
    def export_posts(self, request, queryset):
        """Экспорт постов в JSON"""
        posts_data = []
        for post in queryset:
            post_data = {
                'title': post.safe_translation_getter('title', any_language=True),
                'slug': post.safe_translation_getter('slug', any_language=True),
                'content': post.safe_translation_getter('content', any_language=True),
                'excerpt': post.safe_translation_getter('excerpt', any_language=True),
                'status': post.status,
                'is_featured': post.is_featured,
                'allow_comments': post.allow_comments,
                'views_count': post.views_count,
                'reading_time': post.reading_time,
                'created_at': post.created_at.isoformat(),
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'author': post.author.username if post.author else None,
                'category': post.category.safe_translation_getter('name', any_language=True) if post.category else None,
                'meta_title': post.safe_translation_getter('meta_title', any_language=True),
                'meta_description': post.safe_translation_getter('meta_description', any_language=True),
                'meta_keywords': post.safe_translation_getter('meta_keywords', any_language=True),
                'tags': [tag.name for tag in post.tags.all()],
                'comments_count': post.comments.count(),
                'images_count': post.images.count(),
            }
            posts_data.append(post_data)
        
        response = HttpResponse(
            json.dumps(posts_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="blog_posts_export.json"'
        return response
    export_posts.short_description = "📥 Export selected posts"
    
    def seo_audit(self, request, queryset):
        """SEO аудит постов"""
        audit_results = []
        
        for post in queryset:
            issues = []
            score = 0
            
            # Проверяем заголовок
            title = post.safe_translation_getter('meta_title', any_language=True) or post.safe_translation_getter('title', any_language=True)
            if not title:
                issues.append('No title')
            elif len(title) < 30 or len(title) > 60:
                issues.append('Title length should be 30-60 chars')
            else:
                score += 25
            
            # Проверяем описание
            description = post.safe_translation_getter('meta_description', any_language=True)
            if not description:
                issues.append('No meta description')
            elif len(description) < 120 or len(description) > 160:
                issues.append('Description length should be 120-160 chars')
            else:
                score += 25
            
            # Проверяем изображение
            if not post.featured_image:
                issues.append('No featured image')
            else:
                score += 20
            
            # Проверяем slug
            if not post.safe_translation_getter('slug', any_language=True):
                issues.append('No URL slug')
            else:
                score += 15
            
            # Проверяем ключевые слова
            if not post.safe_translation_getter('meta_keywords', any_language=True):
                issues.append('No meta keywords')
            else:
                score += 15
            
            audit_results.append({
                'post': post.safe_translation_getter('title', any_language=True) or f'Post {post.pk}',
                'score': score,
                'issues': issues
            })
        
        # Формируем отчет
        report_html = '<div style="font-family: Arial, sans-serif; max-width: 800px;">'
        report_html += '<h2 style="color: #0073aa;">🔍 SEO Audit Report</h2>'
        
        for result in audit_results:
            color = '#46b450' if result['score'] >= 80 else '#f56e28' if result['score'] >= 60 else '#dc3232'
            report_html += f'''
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; color: {color};">
                    {result['post']} - Score: {result['score']}/100
                </h3>
                <div style="color: #666;">
                    Issues: {', '.join(result['issues']) if result['issues'] else 'All good!'}
                </div>
            </div>
            '''
        
        report_html += '</div>'
        
        return render(request, 'admin/seo_audit_report.html', {
            'title': 'SEO Audit Report',
            'report_html': mark_safe(report_html),
            'audit_results': audit_results
        })
    seo_audit.short_description = "🔍 Run SEO audit"
    
    def generate_social_images(self, request, queryset):
        """Генерация изображений для соцсетей (заглушка)"""
        # В реальном проекте здесь была бы логика генерации изображений
        count = queryset.count()
        messages.info(request, f'📱 Social media images generation queued for {count} post{"s" if count != 1 else ""}. '
                              f'This feature requires additional setup.')
    generate_social_images.short_description = "📱 Generate social images"
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем автора при создании"""
        if not change:  # Если создается новый пост
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    # Дополнительные URL-ы для быстрых действий
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/quick-publish/', self.admin_site.admin_view(self.quick_publish_view), name='blog_blogpost_quick_publish'),
            path('<path:object_id>/quick-draft/', self.admin_site.admin_view(self.quick_draft_view), name='blog_blogpost_quick_draft'),
            path('<path:object_id>/duplicate/', self.admin_site.admin_view(self.duplicate_view), name='blog_blogpost_duplicate'),
        ]
        return custom_urls + urls
    
    @staff_member_required
    def quick_publish_view(self, request, object_id):
        """Быстрая публикация поста"""
        try:
            post = BlogPost.objects.get(pk=object_id)
            post.status = 'published'
            if not post.published_at:
                post.published_at = timezone.now()
            post.save()
            messages.success(request, f'🚀 Post "{post.safe_translation_getter("title", any_language=True)}" published!')
        except BlogPost.DoesNotExist:
            messages.error(request, '❌ Post not found.')
        
        return redirect('admin:blog_blogpost_changelist')
    
    @staff_member_required
    def quick_draft_view(self, request, object_id):
        """Быстрое перемещение в черновики"""
        try:
            post = BlogPost.objects.get(pk=object_id)
            post.status = 'draft'
            post.save()
            messages.warning(request, f'📝 Post "{post.safe_translation_getter("title", any_language=True)}" moved to draft.')
        except BlogPost.DoesNotExist:
            messages.error(request, '❌ Post not found.')
        
        return redirect('admin:blog_blogpost_changelist')
    
    @staff_member_required
    def duplicate_view(self, request, object_id):
        """Дублирование одного поста"""
        try:
            original_post = BlogPost.objects.get(pk=object_id)
            original_title = original_post.safe_translation_getter('title', any_language=True) or f'Post {original_post.pk}'
            
            # Дублируем пост
            original_post.pk = None
            original_post.slug = None
            original_post.status = 'draft'
            original_post.published_at = None
            original_post.views_count = 0
            original_post.save()
            
            # Обновляем переводы
            for translation in original_post.translations.all():
                translation.pk = None
                translation.master = original_post
                translation.title = f'Copy of {translation.title}' if translation.title else f'Copy of {original_title}'
                translation.slug = None
                translation.save()
            
            messages.success(request, f'📄 Post duplicated successfully! Edit the new draft.')
            return redirect('admin:blog_blogpost_change', original_post.pk)
            
        except BlogPost.DoesNotExist:
            messages.error(request, '❌ Post not found.')
            return redirect('admin:blog_blogpost_changelist')
    
    class Media:
        css = {'all': ('/static/admin/css/custom_admin.css',)}
        js = ('/static/admin/js/custom_admin.js',)


# Конец Части 2 - продолжение в Части 3
# ЧАСТЬ 3 из 3 - Comment, Image Admin и настройки (финал admin.py)

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin, WordPressStyleAdminMixin):
    """WordPress-стиль админка для комментариев - как в WP Comments"""
    list_display = (
        'comment_avatar', 'get_author_info', 'get_post_info', 
        'content_preview', 'approval_status', 'comment_meta', 'comment_actions'
    )
    list_filter = (
        'is_approved', 'created_at', 'post__category', 
        'post__status', 'post__is_featured'
    )
    search_fields = (
        'name', 'email', 'content', 
        'post__translations__title', 'post__author__username'
    )
    readonly_fields = (
        'comment_full_preview', 'spam_check_results', 'comment_thread_view',
        'created_at', 'updated_at', 'author_history'
    )
    actions = [
        'approve_comments', 'unapprove_comments', 'mark_as_spam', 
        'bulk_delete', 'export_comments', 'author_whitelist'
    ]
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    # WordPress-стиль fieldsets
    fieldsets = (
        ('💬 Comment Details', {
            'fields': ('post', 'name', 'email', 'comment_full_preview'),
            'classes': ('wp-box', 'wp-box-primary'),
            'description': 'Basic comment information and content'
        }),
        ('📝 Comment Content', {
            'fields': ('content',),
            'classes': ('wp-box', 'wp-box-content'),
            'description': 'Full comment text content'
        }),
        ('⚙️ Moderation Settings', {
            'fields': ('is_approved', 'spam_check_results'),
            'classes': ('wp-box', 'wp-box-moderation'),
            'description': 'Comment approval and spam detection results'
        }),
        ('🧵 Comment Thread', {
            'fields': ('comment_thread_view',),
            'classes': ('wp-box', 'wp-box-thread', 'collapse'),
            'description': 'View this comment in the context of the full conversation'
        }),
        ('👤 Author Information', {
            'fields': ('author_history',),
            'classes': ('wp-box', 'wp-box-author', 'collapse'),
            'description': 'Comment author history and statistics'
        }),
        ('📊 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('wp-box', 'wp-box-meta', 'collapse'),
            'description': 'Comment creation and modification dates'
        }),
    )
    
    def comment_avatar(self, obj):
        """Аватар автора комментария как в WordPress"""
        # Генерируем аватар по email или имени
        initial = obj.name[0].upper() if obj.name else '?'
        # Простая цветовая схема основанная на email/имени
        hash_base = obj.email if obj.email else obj.name if obj.name else 'anonymous'
        colors = [
            '#0073aa', '#46b450', '#dc3232', '#f56e28', 
            '#82878c', '#ffb900', '#826eb4', '#ea4c89'
        ]
        color = colors[hash(hash_base) % len(colors)]
        
        return format_html(
            '<div class="wp-comment-avatar" style="position: relative;">'
            '<div style="width: 40px; height: 40px; background: linear-gradient(135deg, {}, {}); '
            'color: white; border-radius: 50%; display: flex; align-items: center; '
            'justify-content: center; font-weight: bold; font-size: 16px; '
            'border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.15); '
            'transition: all 0.2s ease;" '
            'onmouseover="this.style.transform=\'scale(1.1)\';"'
            'onmouseout="this.style.transform=\'scale(1)\';">{}</div>'
            '{}'
            '</div>',
            color, color + '80', initial,
            '<div style="position: absolute; bottom: -2px; right: -2px; '
            'background: {}; color: white; border-radius: 50%; '
            'width: 16px; height: 16px; display: flex; align-items: center; '
            'justify-content: center; font-size: 8px; border: 2px solid white;">{}</div>'.format(
                '#46b450' if obj.is_approved else '#f56e28',
                '✓' if obj.is_approved else '⏳'
            )
        )
    comment_avatar.short_description = ''
    
    def get_author_info(self, obj):
        """Информация об авторе комментария"""
        # Подсчитываем статистику автора
        author_comments = BlogComment.objects.filter(email=obj.email) if obj.email else BlogComment.objects.filter(name=obj.name)
        total_comments = author_comments.count()
        approved_comments = author_comments.filter(is_approved=True).count()
        
        # Определяем статус автора
        if approved_comments > 10:
            author_status, status_color = 'Trusted', '#46b450'
        elif approved_comments > 3:
            author_status, status_color = 'Regular', '#0073aa'
        elif approved_comments > 0:
            author_status, status_color = 'New', '#f56e28'
        else:
            author_status, status_color = 'First Time', '#82878c'
        
        return format_html(
            '<div class="wp-comment-author" style="display: flex; flex-direction: column; gap: 3px;">'
            '<div style="font-weight: bold; color: #0073aa; font-size: 13px;">{}</div>'
            '<div style="font-size: 11px; color: #666; font-family: monospace;">{}</div>'
            '<div style="display: flex; gap: 5px; align-items: center;">'
            '{}'
            '<span style="font-size: 9px; color: #999;">{} comment{}</span>'
            '</div>'
            '</div>',
            obj.name or 'Anonymous',
            obj.email or 'No email',
            self.get_wordpress_badge(author_status, status_color.replace('#', ''), '👤'),
            total_comments,
            's' if total_comments != 1 else ''
        )
    get_author_info.short_description = 'Author'
    get_author_info.admin_order_field = 'name'
    
    def get_post_info(self, obj):
        """Информация о посте"""
        post_title = obj.post.safe_translation_getter('title', any_language=True) or f'Post {obj.post.pk}'
        post_comments_count = obj.post.comments.filter(is_approved=True).count()
        
        # Статус поста
        status_config = {
            'published': {'color': '#46b450', 'icon': '✓'},
            'draft': {'color': '#82878c', 'icon': '📝'},
            'scheduled': {'color': '#0073aa', 'icon': '⏰'}
        }
        config = status_config.get(obj.post.status, status_config['draft'])
        
        return format_html(
            '<div class="wp-comment-post" style="display: flex; flex-direction: column; gap: 3px;">'
            '<div style="font-weight: bold; color: #0073aa; font-size: 13px; max-width: 200px;" title="{}">'
            '<a href="{}" style="color: #0073aa; text-decoration: none;">{}</a>'
            '</div>'
            '<div style="display: flex; gap: 5px; align-items: center;">'
            '{}'
            '<span style="font-size: 9px; color: #999;">{} total comments</span>'
            '</div>'
            '<div style="font-size: 10px; color: #666;">by {}</div>'
            '</div>',
            post_title,
            reverse('admin:blog_blogpost_change', args=[obj.post.pk]),
            post_title[:30] + '...' if len(post_title) > 30 else post_title,
            self.get_wordpress_badge(obj.post.get_status_display(), config['color'].replace('#', ''), config['icon']),
            post_comments_count,
            obj.post.author.username if obj.post.author else 'Unknown'
        )
    get_post_info.short_description = 'Post'
    get_post_info.admin_order_field = 'post__translations__title'
    
    def content_preview(self, obj):
        """Превью содержимого комментария"""
        preview_length = 100
        content = obj.content
        word_count = len(content.split())
        char_count = len(content)
        
        # Обрезаем контент для превью
        if len(content) > preview_length:
            preview = content[:preview_length].rsplit(' ', 1)[0] + '...'
        else:
            preview = content
        
        # Определяем "настроение" комментария (примерный анализ)
        positive_words = ['good', 'great', 'excellent', 'love', 'amazing', 'perfect', 'thank']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'worst', 'stupid', 'spam']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment_color, sentiment_icon = '#46b450', '😊'
        elif negative_count > positive_count:
            sentiment_color, sentiment_icon = '#f56e28', '😐'
        else:
            sentiment_color, sentiment_icon = '#82878c', '😶'
        
        return format_html(
            '<div class="wp-comment-preview" style="max-width: 300px;">'
            '<div style="background: #f9f9f9; padding: 10px; border-radius: 6px; '
            'border-left: 3px solid {}; font-size: 13px; line-height: 1.4; '
            'color: #444; margin-bottom: 6px; position: relative;" title="{}">'
            '"{}"'
            '<div style="position: absolute; top: 4px; right: 6px; font-size: 16px;">{}</div>'
            '</div>'
            '<div style="display: flex; gap: 8px; font-size: 10px; color: #999;">'
            '<span>📝 {} words</span>'
            '<span>🔤 {} chars</span>'
            '<span>📅 {}</span>'
            '</div>'
            '</div>',
            sentiment_color,
            content,  # полный контент для tooltip
            preview,
            sentiment_icon,
            word_count,
            char_count,
            obj.created_at.strftime('%b %d')
        )
    content_preview.short_description = 'Comment Content'
    
    def approval_status(self, obj):
        """Статус одобрения с дополнительной информацией"""
        if obj.is_approved:
            time_since_approved = timezone.now() - obj.updated_at
            days_ago = time_since_approved.days
            
            return format_html(
                '<div class="wp-approval-status" style="text-align: center;">'
                '{}'
                '<div style="font-size: 9px; color: #46b450; margin-top: 3px; font-weight: bold;">'
                'LIVE{}</div>'
                '</div>',
                self.get_wordpress_badge('Approved', 'green', '✓'),
                f' • {days_ago}d ago' if days_ago > 0 else ''
            )
        else:
            time_since_created = timezone.now() - obj.created_at
            hours_ago = int(time_since_created.total_seconds() / 3600)
            
            return format_html(
                '<div class="wp-approval-status" style="text-align: center;">'
                '{}'
                '<div style="font-size: 9px; color: #f56e28; margin-top: 3px; font-weight: bold;">'
                'PENDING{}</div>'
                '</div>',
                self.get_wordpress_badge('Pending', 'orange', '⏳'),
                f' • {hours_ago}h ago' if hours_ago > 0 else ' • New'
            )
    approval_status.short_description = 'Status'
    approval_status.admin_order_field = 'is_approved'
    
    def comment_meta(self, obj):
        """Мета-информация комментария"""
        # IP-адрес (если есть)
        ip_display = getattr(obj, 'ip_address', 'Unknown IP')
        
        # User Agent (если есть)
        user_agent = getattr(obj, 'user_agent', '')
        browser_info = 'Unknown Browser'
        if 'Chrome' in user_agent:
            browser_info = '🌐 Chrome'
        elif 'Firefox' in user_agent:
            browser_info = '🦊 Firefox'
        elif 'Safari' in user_agent:
            browser_info = '🧭 Safari'
        elif 'Edge' in user_agent:
            browser_info = '🔷 Edge'
        
        return format_html(
            '<div class="wp-comment-meta" style="font-size: 10px; color: #666; text-align: center;">'
            '<div style="margin-bottom: 3px;">{}</div>'
            '<div style="margin-bottom: 3px;">🌍 {}</div>'
            '<div>{}</div>'
            '</div>',
            browser_info,
            ip_display[:15] + '...' if len(ip_display) > 15 else ip_display,
            obj.created_at.strftime('%H:%M')
        )
    comment_meta.short_description = 'Meta'
    
    def comment_actions(self, obj):
        """Действия для комментария"""
        if obj.pk:
            actions = []
            
            # Approve/Unapprove
            if not obj.is_approved:
                actions.append(
                    self.get_wordpress_button('Approve', f'/admin/blog/blogcomment/{obj.pk}/approve/', 'success', '✓')
                )
            else:
                actions.append(
                    self.get_wordpress_button('Unapprove', f'/admin/blog/blogcomment/{obj.pk}/unapprove/', 'warning', '❌')
                )
            
            # Edit
            actions.append(
                self.get_wordpress_button('Edit', f'/admin/blog/blogcomment/{obj.pk}/change/', 'secondary', '✏️')
            )
            
            # Reply (заглушка)
            actions.append(
                self.get_wordpress_button('Reply', '#', 'secondary', '💬')
            )
            
            # Spam
            actions.append(
                self.get_wordpress_button('Spam', f'/admin/blog/blogcomment/{obj.pk}/spam/', 'danger', '🚫')
            )
            
            return format_html(
                '<div class="wp-comment-actions" style="display: flex; flex-direction: column; gap: 2px;">'
                '{}'
                '</div>',
                ''.join(actions)
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    comment_actions.short_description = 'Actions'
    
    # Readonly поля для детальной информации
    def comment_full_preview(self, obj):
        """Полный превью комментария"""
        if not obj.pk:
            return format_html('<p style="color: #999;">Save comment to see full preview</p>')
        
        return format_html(
            '<div class="wp-comment-full" style="background: white; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
            '<div style="display: flex; gap: 15px; margin-bottom: 15px;">'
            '<div style="flex-shrink: 0;">{}</div>'
            '<div style="flex: 1;">'
            '<div style="font-weight: bold; color: #0073aa; margin-bottom: 5px;">{}</div>'
            '<div style="font-size: 12px; color: #666; margin-bottom: 10px;">{} • {}</div>'
            '</div>'
            '</div>'
            '<div style="background: #f9f9f9; padding: 15px; border-radius: 6px; '
            'border-left: 4px solid #0073aa; line-height: 1.6; color: #444;">{}</div>'
            '</div>',
            self.comment_avatar(obj),
            obj.name or 'Anonymous',
            obj.email or 'No email',
            obj.created_at.strftime('%B %d, %Y at %H:%M'),
            obj.content.replace('\n', '<br>')
        )
    comment_full_preview.short_description = 'Full Comment Preview'
    
    def spam_check_results(self, obj):
        """Результаты проверки на спам"""
        if not obj.pk:
            return format_html('<p style="color: #999;">Save comment to see spam check results</p>')
        
        # Простая проверка на спам (в реальном проекте используйте Akismet или подобные сервисы)
        spam_indicators = []
        spam_score = 0
        
        # Проверяем подозрительные паттерны
        content_lower = obj.content.lower()
        
        # Много ссылок
        link_count = obj.content.count('http')
        if link_count > 2:
            spam_indicators.append(f'Multiple links ({link_count})')
            spam_score += 30
        
        # Подозрительные слова
        spam_words = ['free', 'buy now', 'click here', 'make money', 'casino', 'pills']
        found_spam_words = [word for word in spam_words if word in content_lower]
        if found_spam_words:
            spam_indicators.append(f'Spam keywords: {", ".join(found_spam_words)}')
            spam_score += 20 * len(found_spam_words)
        
        # Много заглавных букв
        caps_ratio = sum(1 for c in obj.content if c.isupper()) / len(obj.content) if obj.content else 0
        if caps_ratio > 0.3:
            spam_indicators.append('Excessive caps')
            spam_score += 25
        
        # Определяем уровень риска
        if spam_score >= 50:
            risk_level, risk_color, risk_icon = 'High Risk', '#dc3232', '🚨'
        elif spam_score >= 25:
            risk_level, risk_color, risk_icon = 'Medium Risk', '#f56e28', '⚠️'
        elif spam_score > 0:
            risk_level, risk_color, risk_icon = 'Low Risk', '#ffb900', '🟡'
        else:
            risk_level, risk_color, risk_icon = 'Clean', '#46b450', '✅'
        
        return format_html(
            '<div class="wp-spam-check" style="background: white; padding: 15px; '
            'border-radius: 6px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 10px 0; color: #0073aa;">🛡️ Spam Detection Results</h4>'
            '<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">'
            '<div style="font-size: 24px;">{}</div>'
            '<div>'
            '<div style="font-weight: bold; color: {}; font-size: 14px;">{}</div>'
            '<div style="font-size: 12px; color: #666;">Score: {}/100</div>'
            '</div>'
            '</div>'
            '{}'
            '</div>',
            risk_icon, risk_color, risk_level, spam_score,
            '<div style="background: #f9f9f9; padding: 10px; border-radius: 4px; '
            'font-size: 12px; color: #666;"><strong>Issues found:</strong><br>{}</div>'.format(
                '<br>'.join(f'• {indicator}' for indicator in spam_indicators)
            ) if spam_indicators else '<div style="color: #46b450; font-size: 12px;">✅ No spam indicators detected</div>'
        )
    spam_check_results.short_description = 'Spam Check'
    
    def comment_thread_view(self, obj):
        """Просмотр треда комментариев"""
        if not obj.pk:
            return format_html('<p style="color: #999;">Save comment to see thread</p>')
        
        # Получаем все комментарии к этому посту
        all_comments = obj.post.comments.order_by('created_at')
        current_index = list(all_comments.values_list('pk', flat=True)).index(obj.pk) + 1
        
        # Показываем контекст (2 комментария до и после)
        start_index = max(0, current_index - 3)
        end_index = min(len(all_comments), current_index + 2)
        context_comments = all_comments[start_index:end_index]
        
        thread_html = '<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e1e1e1;">'
        thread_html += f'<h4 style="margin: 0 0 15px 0; color: #0073aa;">💬 Comment Thread (#{current_index} of {len(all_comments)})</h4>'
        
        for i, comment in enumerate(context_comments):
            is_current = comment.pk == obj.pk
            bg_color = '#e3f2fd' if is_current else '#f9f9f9'
            border_color = '#0073aa' if is_current else '#e1e1e1'
            
            thread_html += f'''
            <div style="background: {bg_color}; padding: 12px; margin: 8px 0; 
                        border-radius: 6px; border-left: 4px solid {border_color};">
                <div style="display: flex; justify-content: between; margin-bottom: 8px;">
                    <strong style="color: #0073aa;">{comment.name or "Anonymous"}</strong>
                    <span style="font-size: 11px; color: #666; margin-left: auto;">
                        {comment.created_at.strftime("%b %d, %H:%M")}
                        {" (THIS COMMENT)" if is_current else ""}
                    </span>
                </div>
                <div style="font-size: 13px; line-height: 1.4; color: #444;">
                    {comment.content[:200] + "..." if len(comment.content) > 200 else comment.content}
                </div>
                <div style="margin-top: 6px;">
                    {"✅ Approved" if comment.is_approved else "⏳ Pending"}
                </div>
            </div>
            '''
        
        thread_html += '</div>'
        return format_html(thread_html)
    comment_thread_view.short_description = 'Comment Thread'
    
    def author_history(self, obj):
        """История автора комментариев"""
        if not obj.email:
            return format_html('<p style="color: #999;">No email - cannot track author history</p>')
        
        # Получаем все комментарии этого автора
        author_comments = BlogComment.objects.filter(email=obj.email).order_by('-created_at')
        total_comments = author_comments.count()
        approved_comments = author_comments.filter(is_approved=True).count()
        pending_comments = total_comments - approved_comments
        
        # Последние посты
        recent_posts = set()
        for comment in author_comments[:10]:
            post_title = comment.post.safe_translation_getter('title', any_language=True)
            if post_title:
                recent_posts.add(post_title[:30] + '...' if len(post_title) > 30 else post_title)
        
        return format_html(
            '<div class="wp-author-history" style="background: white; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 15px 0; color: #0073aa;">👤 Author History: {}</h4>'
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin-bottom: 15px;">'
            '{}'
            '{}'
            '{}'
            '</div>'
            '<div style="background: #f9f9f9; padding: 12px; border-radius: 6px;">'
            '<h5 style="margin: 0 0 8px 0; color: #0073aa;">Recent Posts Commented On:</h5>'
            '<div style="font-size: 12px; color: #666;">{}</div>'
            '</div>'
            '</div>',
            obj.email,
            self.get_wordpress_stat_card(total_comments, 'Total', 'blue', '💬'),
            self.get_wordpress_stat_card(approved_comments, 'Approved', 'green', '✅'),
            self.get_wordpress_stat_card(pending_comments, 'Pending', 'orange', '⏳'),
            '<br>'.join(f'• {post}' for post in list(recent_posts)[:5]) if recent_posts else 'No recent comments'
        )
    author_history.short_description = 'Author History'
    
    # WordPress-стиль действия
    def approve_comments(self, request, queryset):
        count = queryset.update(is_approved=True)
        messages.success(request, f'✅ {count} comment{"s" if count != 1 else ""} approved!')
    approve_comments.short_description = "✅ Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        count = queryset.update(is_approved=False)
        messages.warning(request, f'❌ {count} comment{"s" if count != 1 else ""} unapproved.')
    unapprove_comments.short_description = "❌ Unapprove selected comments"
    
    def mark_as_spam(self, request, queryset):
        # В реальном проекте здесь была бы отправка в спам-фильтр
        count = queryset.count()
        queryset.delete()
        messages.warning(request, f'🚫 {count} comment{"s" if count != 1 else ""} marked as spam and deleted.')
    mark_as_spam.short_description = "🚫 Mark as spam"
    
    def bulk_delete(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        messages.error(request, f'🗑️ {count} comment{"s" if count != 1 else ""} deleted.')
    bulk_delete.short_description = "🗑️ Delete selected comments"
    
    def export_comments(self, request, queryset):
        """Экспорт комментариев"""
        comments_data = []
        for comment in queryset:
            comments_data.append({
                'post_title': comment.post.safe_translation_getter('title', any_language=True),
                'author_name': comment.name,
                'author_email': comment.email,
                'content': comment.content,
                'is_approved': comment.is_approved,
                'created_at': comment.created_at.isoformat(),
                'post_url': comment.post.safe_translation_getter('slug', any_language=True),
            })
        
        response = HttpResponse(
            json.dumps(comments_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="blog_comments_export.json"'
        return response
    export_comments.short_description = "📥 Export selected comments"
    
    def author_whitelist(self, request, queryset):
        """Добавление авторов в белый список (заглушка)"""
        unique_emails = set()
        for comment in queryset:
            if comment.email:
                unique_emails.add(comment.email)
        
        # В реальном проекте здесь была бы логика добавления в whitelist
        messages.info(request, f'📋 {len(unique_emails)} unique author{"s" if len(unique_emails) != 1 else ""} would be added to whitelist. Feature requires implementation.')
    author_whitelist.short_description = "📋 Add authors to whitelist"
    
    class Media:
        css = {'all': ('/static/admin/css/custom_admin.css',)}
        js = ('/static/admin/js/custom_admin.js',)


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin, WordPressStyleAdminMixin):
    """WordPress-стиль админка для изображений - как WordPress Media Library"""
    list_display = (
        'image_thumbnail', 'get_image_info', 'get_post_info', 
        'image_details', 'image_meta', 'image_actions'
    )
    list_filter = ('created_at', 'post__category', 'post__status')
    search_fields = ('alt_text', 'caption', 'post__translations__title')
    readonly_fields = ('image_large_preview', 'image_technical_info', 'created_at')
    list_per_page = 30
    
    # WordPress-стиль fieldsets
    fieldsets = (
        ('🖼️ Image Upload', {
            'fields': ('image', 'image_large_preview'),
            'classes': ('wp-box', 'wp-box-primary'),
            'description': 'Upload and preview your image'
        }),
        ('📝 Image Details', {
            'fields': ('post', 'alt_text', 'caption'),
            'classes': ('wp-box', 'wp-box-secondary'),
            'description': 'Image description and caption for accessibility and SEO'
        }),
        ('🔧 Technical Information', {
            'fields': ('image_technical_info', 'created_at'),
            'classes': ('wp-box', 'wp-box-technical', 'collapse'),
            'description': 'Technical details about the uploaded image'
        }),
    )
    
    def image_thumbnail(self, obj):
        """Thumbnail изображения как в WordPress Media Library"""
        if obj.image:
            return format_html(
                '<div class="wp-media-thumbnail" style="position: relative; border-radius: 8px; '
                'overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.15); background: white;">'
                '<img src="{}" style="width: 80px; height: 60px; object-fit: cover; '
                'transition: all 0.3s ease;" '
                'onmouseover="this.style.transform=\'scale(1.05)\';"'
                'onmouseout="this.style.transform=\'scale(1)\';" />'
                '<div style="position: absolute; top: 4px; right: 4px; '
                'background: rgba(0,115,170,0.9); color: white; border-radius: 3px; '
                'padding: 2px 6px; font-size: 9px; font-weight: bold;">📷 IMG</div>'
                '<div style="position: absolute; bottom: 2px; left: 2px; right: 2px; '
                'background: linear-gradient(transparent, rgba(0,0,0,0.8)); '
                'color: white; font-size: 8px; padding: 4px 2px; text-align: center; '
                'border-radius: 0 0 6px 6px;">{}</div>'
                '</div>',
                obj.image.url,
                obj.alt_text[:20] + '...' if obj.alt_text and len(obj.alt_text) > 20 else obj.alt_text or 'No alt text'
            )
        return format_html(
            '<div class="wp-media-placeholder" style="width: 80px; height: 60px; '
            'background: linear-gradient(135deg, #f1f1f1, #e1e1e1); border-radius: 8px; '
            'display: flex; align-items: center; justify-content: center; '
            'border: 2px dashed #ddd; color: #999;">'
            '<span style="font-size: 24px;">📷</span>'
            '</div>'
        )
    image_thumbnail.short_description = ''
    
    def get_image_info(self, obj):
        """Информация об изображении"""
        if obj.image:
            try:
                # Получаем размеры изображения
                from PIL import Image
                import os
                
                image_path = obj.image.path
                if os.path.exists(image_path):
                    with Image.open(image_path) as img:
                        width, height = img.size
                        file_size = os.path.getsize(image_path)
                        file_size_mb = file_size / (1024 * 1024)
                        
                        # Определяем качество изображения
                        total_pixels = width * height
                        if total_pixels > 2000000:  # > 2MP
                            quality_color, quality_text = '#46b450', 'High Res'
                        elif total_pixels > 500000:  # > 0.5MP
                            quality_color, quality_text = '#0073aa', 'Good'
                        else:
                            quality_color, quality_text = '#f56e28', 'Low Res'
                else:
                    width = height = 0
                    file_size_mb = 0
                    quality_color, quality_text = '#dc3232', 'Missing'
            except Exception:
                width = height = 0
                file_size_mb = 0
                quality_color, quality_text = '#82878c', 'Unknown'
            
            return format_html(
                '<div class="wp-image-info" style="display: flex; flex-direction: column; gap: 3px;">'
                '<div style="font-weight: bold; color: #0073aa; font-size: 13px;">{} × {}</div>'
                '<div style="font-size: 11px; color: #666;">{:.1f} MB</div>'
                '<div>{}</div>'
                '</div>',
                width, height, file_size_mb,
                self.get_wordpress_badge(quality_text, quality_color.replace('#', ''), '🖼️')
            )
        return format_html('<span style="color: #dc3232;">No image</span>')
    get_image_info.short_description = 'Image Info'
    
    def get_post_info(self, obj):
        """Информация о посте"""
        if obj.post:
            post_title = obj.post.safe_translation_getter('title', any_language=True) or f'Post {obj.post.pk}'
            post_images_count = obj.post.images.count()
            
            return format_html(
                '<div class="wp-image-post" style="display: flex; flex-direction: column; gap: 3px;">'
                '<div style="font-weight: bold; color: #0073aa; font-size: 13px; max-width: 180px;" title="{}">'
                '<a href="{}" style="color: #0073aa; text-decoration: none;">{}</a>'
                '</div>'
                '<div style="font-size: 11px; color: #666;">{} image{} total</div>'
                '<div style="font-size: 10px; color: #999;">by {}</div>'
                '</div>',
                post_title,
                reverse('admin:blog_blogpost_change', args=[obj.post.pk]),
                post_title[:25] + '...' if len(post_title) > 25 else post_title,
                post_images_count,
                's' if post_images_count != 1 else '',
                obj.post.author.username if obj.post.author else 'Unknown'
            )
        return format_html('<span style="color: #f56e28; font-style: italic;">Unattached</span>')
    get_post_info.short_description = 'Attached to'
    get_post_info.admin_order_field = 'post__translations__title'
    
    def image_details(self, obj):
        """Детали изображения"""
        alt_text_length = len(obj.alt_text) if obj.alt_text else 0
        caption_length = len(obj.caption) if obj.caption else 0
        
        # SEO оценка
        seo_score = 0
        if obj.alt_text:
            if 5 <= alt_text_length <= 125:
                seo_score += 50
            else:
                seo_score += 20
        
        if obj.caption:
            seo_score += 30
        
        if obj.alt_text and obj.caption:
            seo_score += 20
        
        # Определяем SEO статус
        if seo_score >= 80:
            seo_color, seo_text = '#46b450', 'Excellent'
        elif seo_score >= 50:
            seo_color, seo_text = '#f56e28', 'Good'
        else:
            seo_color, seo_text = '#dc3232', 'Poor'
        
        return format_html(
            '<div class="wp-image-details" style="text-align: center; '
            'background: linear-gradient(135deg, #f9f9f9, #f1f1f1); padding: 10px; '
            'border-radius: 6px; border: 1px solid #e1e1e1;">'
            '<div style="margin-bottom: 8px;">{}</div>'
            '<div style="display: flex; justify-content: center; gap: 8px; margin-bottom: 6px;">'
            '<div style="text-align: center;">'
            '<div style="font-size: 12px; font-weight: bold; color: #0073aa;">{}</div>'
            '<div style="font-size: 8px; color: #666;">ALT TEXT</div>'
            '</div>'
            '<div style="text-align: center;">'
            '<div style="font-size: 12px; font-weight: bold; color: #82878c;">{}</div>'
            '<div style="font-size: 8px; color: #666;">CAPTION</div>'
            '</div>'
            '</div>'
            '<div style="font-size: 8px; color: {}; font-weight: bold; text-transform: uppercase;">'
            '🔍 {} SEO</div>'
            '</div>',
            self.get_wordpress_badge(f'{seo_score}%', seo_color.replace('#', ''), '📊'),
            alt_text_length, caption_length, seo_color, seo_text
        )
    image_details.short_description = 'SEO Details'
    
    def image_meta(self, obj):
        """Мета-информация изображения"""
        upload_date = obj.created_at
        days_ago = (timezone.now() - upload_date).days
        
        return format_html(
            '<div class="wp-image-meta" style="font-size: 10px; color: #666; text-align: center;">'
            '<div style="margin-bottom: 3px;">📅 {}</div>'
            '<div style="margin-bottom: 3px;">⏰ {} day{} ago</div>'
            '<div>🆔 #{}</div>'
            '</div>',
            upload_date.strftime('%b %d'),
            days_ago,
            's' if days_ago != 1 else '',
            obj.pk
        )
    image_meta.short_description = 'Meta'
    
    def image_actions(self, obj):
        """Действия для изображения"""
        if obj.pk:
            actions = []
            
            # Edit
            actions.append(
                self.get_wordpress_button('Edit', f'/admin/blog/blogimage/{obj.pk}/change/', 'primary', '✏️')
            )
            
            # View
            if obj.image:
                actions.append(
                    self.get_wordpress_button('View', obj.image.url, 'secondary', '👁️', '_blank')
                )
            
            # Copy URL (JavaScript)
            if obj.image:
                actions.append(
                    self.get_wordpress_button('Copy URL', f'javascript:navigator.clipboard.writeText("{obj.image.url}")', 'secondary', '📋')
                )
            
            # Delete
            actions.append(
                self.get_wordpress_button('Delete', f'/admin/blog/blogimage/{obj.pk}/delete/', 'danger', '🗑️')
            )
            
            return format_html(
                '<div class="wp-image-actions" style="display: flex; flex-direction: column; gap: 2px;">'
                '{}'
                '</div>',
                ''.join(actions)
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    image_actions.short_description = 'Actions'
    
    # Readonly поля
    def image_large_preview(self, obj):
        """Большой превью изображения"""
        if obj.image:
            return format_html(
                '<div class="wp-image-large-preview" style="text-align: center; '
                'background: white; padding: 20px; border-radius: 8px; border: 1px solid #e1e1e1;">'
                '<img src="{}" style="max-width: 100%; max-height: 400px; '
                'border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />'
                '<div style="margin-top: 15px; font-size: 12px; color: #666;">'
                '<a href="{}" target="_blank" style="color: #0073aa;">🔗 View full size</a>'
                '</div>'
                '</div>',
                obj.image.url, obj.image.url
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    image_large_preview.short_description = 'Large Preview'
    
    def image_technical_info(self, obj):
        """Техническая информация об изображении"""
        if not obj.image:
            return format_html('<p style="color: #999;">No image uploaded</p>')
        
        try:
            from PIL import Image
            import os
            
            image_path = obj.image.path
            if os.path.exists(image_path):
                with Image.open(image_path) as img:
                    width, height = img.size
                    format_name = img.format
                    mode = img.mode
                    
                file_size = os.path.getsize(image_path)
                file_size_mb = file_size / (1024 * 1024)
                
                # Вычисляем aspect ratio
                gcd = math.gcd(width, height) if width and height else 1
                aspect_w = width // gcd if gcd else width
                aspect_h = height // gcd if gcd else height
                
            else:
                return format_html('<p style="color: #dc3232;">Image file not found</p>')
                
        except Exception as e:
            return format_html('<p style="color: #dc3232;">Error reading image: {}</p>', str(e))
        
        return format_html(
            '<div class="wp-image-technical" style="background: white; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 15px 0; color: #0073aa;">🔧 Technical Information</h4>'
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">'
            '{}'
            '{}'
            '{}'
            '{}'
            '{}'
            '{}'
            '</div>'
            '</div>',
            self.get_wordpress_stat_card(f'{width}×{height}', 'Dimensions', 'blue', '📐'),
            self.get_wordpress_stat_card(f'{file_size_mb:.1f}MB', 'File Size', 'green', '💾'),
            self.get_wordpress_stat_card(format_name or 'Unknown', 'Format', 'orange', '🖼️'),
            self.get_wordpress_stat_card(mode or 'Unknown', 'Color Mode', 'gray', '🎨'),
            self.get_wordpress_stat_card(f'{aspect_w}:{aspect_h}', 'Aspect Ratio', 'blue', '📏'),
            self.get_wordpress_stat_card(obj.image.url.split('/')[-1][:15] + '...', 'Filename', 'gray', '📄')
        )
    image_technical_info.short_description = 'Technical Info'
    
    class Media:
        css = {'all': ('/static/admin/css/custom_admin.css',)}


# Финальные настройки админки в WordPress стиле
admin.site.site_header = "🌍 Abroads Tours - Blog CMS"
admin.site.site_title = "Blog CMS"
admin.site.index_title = "Welcome to WordPress-style Blog Administration"

# Дополнительные настройки
admin.site.enable_nav_sidebar = False  # Отключаем боковую навигацию для более чистого вида

# Кастомный CSS и JS будут подключены через Media классы каждой админки