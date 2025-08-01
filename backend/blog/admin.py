# backend/blog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from .models import BlogPost, Category, BlogImage, BlogComment


class BlogImageInline(admin.TabularInline):
    """Inline для изображений в статье"""
    model = BlogImage
    extra = 1
    fields = ('image', 'alt_text', 'caption')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


class BlogCommentInline(admin.TabularInline):
    """Inline для комментариев"""
    model = BlogComment
    extra = 0
    readonly_fields = ('name', 'email', 'content', 'created_at')
    fields = ('name', 'email', 'content', 'is_approved', 'created_at')
    can_delete = True
    
    def has_add_permission(self, request, obj=None):
        return False  # Комментарии добавляются только через сайт


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    """Админка для категорий с полной поддержкой переводов"""
    list_display = ('get_name', 'get_slug', 'is_active', 'post_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('translations__name', 'translations__description')
    list_editable = ('is_active',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description'),
            'classes': ('wide',)
        }),
        ('Settings', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )
    
    def get_name(self, obj):
        """Получаем переводимое имя"""
        return obj.safe_translation_getter('name', any_language=True) or f'Category {obj.pk}'
    get_name.short_description = 'Name'
    get_name.admin_order_field = 'translations__name'
    
    def get_slug(self, obj):
        """Получаем переводимый slug"""
        slug = obj.safe_translation_getter('slug', any_language=True)
        if slug:
            return format_html('<code>{}</code>', slug)
        return format_html('<span style="color: #999;">no-slug</span>')
    get_slug.short_description = 'Slug'
    get_slug.admin_order_field = 'translations__slug'
    
    def post_count(self, obj):
        """Количество статей в категории"""
        published_count = obj.blogpost_set.filter(status='published').count()
        total_count = obj.blogpost_set.count()
        
        if published_count > 0:
            color = '#28a745'
            text = f'{published_count}/{total_count}'
        else:
            color = '#6c757d'
            text = f'0/{total_count}'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;" title="{} published, {} total">{}</span>',
            color, published_count, total_count, text
        )
    post_count.short_description = 'Posts (Pub/Total)'


@admin.register(BlogPost)
class BlogPostAdmin(TranslatableAdmin):
    """Админка для статей блога - полнофункциональная как в WordPress"""
    
    list_display = (
        'get_title', 'get_slug_preview', 'author', 'category', 
        'status_badge', 'is_featured', 'allow_comments', 'views_count', 
        'published_at', 'preview_link'
    )
    list_filter = (
        'status', 'is_featured', 'category', 'created_at', 
        'published_at', 'allow_comments', 'translations__schema_article_type'
    )
    search_fields = (
        'translations__title', 'translations__content', 
        'translations__meta_description', 'author__username', 
        'author__first_name', 'author__last_name'
    )
    readonly_fields = (
        'views_count', 'created_at', 'updated_at', 
        'preview_link', 'featured_image_preview', 'seo_preview'
    )
    filter_horizontal = ('tags',)
    list_editable = ('is_featured', 'allow_comments')
    list_per_page = 25
    date_hierarchy = 'published_at'
    
    # Группировка полей как в WordPress
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt'),
            'classes': ('wide',),
            'description': 'Main content of your blog post'
        }),
        ('Publishing', {
            'fields': ('status', 'published_at', 'author', 'category'),
            'classes': ('collapse',)
        }),
        ('Featured Image', {
            'fields': ('featured_image', 'featured_image_preview'),
            'classes': ('collapse',)
        }),
        ('Post Settings', {
            'fields': ('is_featured', 'allow_comments', 'reading_time', 'tags'),
            'classes': ('collapse',)
        }),
        ('SEO & Social Media', {
            'fields': (
                'seo_preview',
                'meta_title', 'meta_description', 'meta_keywords',
                'og_title', 'og_description', 'schema_article_type'
            ),
            'classes': ('collapse',),
            'description': 'SEO optimization and social media settings'
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [BlogImageInline, BlogCommentInline]
    
    # Действия как в WordPress
    actions = [
        'make_published', 'make_draft', 'make_scheduled',
        'make_featured', 'remove_featured', 'reset_views'
    ]
    
    def get_title(self, obj):
        """Получаем переводимый заголовок"""
        title = obj.safe_translation_getter('title', any_language=True)
        if title:
            # Ограничиваем длину для отображения
            if len(title) > 50:
                return format_html(
                    '<span title="{}">{}<span style="color: #999;">...</span></span>',
                    title, title[:47]
                )
            return title
        return format_html('<span style="color: #999;">No title</span>')
    get_title.short_description = 'Title'
    get_title.admin_order_field = 'translations__title'
    
    def get_slug_preview(self, obj):
        """Превью slug с ссылкой"""
        slug = obj.safe_translation_getter('slug', any_language=True)
        if slug:
            try:
                url = obj.get_absolute_url()
                return format_html(
                    '<a href="{}" target="_blank" title="View on site"><code>{}</code></a>',
                    url, slug[:30] + '...' if len(slug) > 30 else slug
                )
            except:
                return format_html('<code>{}</code>', slug)
        return format_html('<span style="color: #999;">no-slug</span>')
    get_slug_preview.short_description = 'Slug'
    get_slug_preview.admin_order_field = 'translations__slug'
    
    def status_badge(self, obj):
        """Красивый badge для статуса"""
        colors = {
            'published': '#28a745',
            'draft': '#6c757d',
            'scheduled': '#007bff'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def featured_image_preview(self, obj):
        """Превью изображения"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; '
                'border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.featured_image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    featured_image_preview.short_description = 'Image Preview'
    
    def seo_preview(self, obj):
        """Превью SEO данных"""
        title = obj.safe_translation_getter('meta_title', any_language=True) or obj.safe_translation_getter('title', any_language=True)
        description = obj.safe_translation_getter('meta_description', any_language=True)
        
        if not title and not description:
            return format_html('<span style="color: #999;">No SEO data</span>')
        
        return format_html(
            '<div style="border: 1px solid #ddd; padding: 10px; border-radius: 4px; background: #f9f9f9;">'
            '<div style="color: #1a0dab; font-size: 18px; margin-bottom: 5px;">{}</div>'
            '<div style="color: #545454; font-size: 13px; line-height: 1.4;">{}</div>'
            '</div>',
            title or 'No title',
            description or 'No description'
        )
    seo_preview.short_description = 'SEO Preview'
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем автора"""
        if not change:  # Если создается новая статья
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def preview_link(self, obj):
        """Ссылка на предпросмотр"""
        if obj.pk:
            try:
                slug = obj.safe_translation_getter('slug', any_language=True)
                if slug:
                    url = reverse('blog:post_detail', kwargs={'slug': slug})
                    return format_html(
                        '<a href="{}" target="_blank" class="button" '
                        'style="background: #007cba; color: white; padding: 5px 10px; '
                        'text-decoration: none; border-radius: 3px;">Preview</a>',
                        url
                    )
            except:
                pass
        return format_html('<span style="color: #999;">Save first</span>')
    preview_link.short_description = 'Actions'
    
    # Действия
    def make_published(self, request, queryset):
        count = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'✅ {count} posts published successfully.')
    make_published.short_description = "✅ Publish selected posts"
    
    def make_draft(self, request, queryset):
        count = queryset.update(status='draft')
        self.message_user(request, f'📝 {count} posts moved to draft.')
    make_draft.short_description = "📝 Move to draft"
    
    def make_scheduled(self, request, queryset):
        count = queryset.update(status='scheduled')
        self.message_user(request, f'📅 {count} posts scheduled.')
    make_scheduled.short_description = "📅 Schedule posts"
    
    def make_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'⭐ {count} posts marked as featured.')
    make_featured.short_description = "⭐ Mark as featured"
    
    def remove_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'🔄 {count} posts removed from featured.')
    remove_featured.short_description = "🔄 Remove from featured"
    
    def reset_views(self, request, queryset):
        count = queryset.update(views_count=0)
        self.message_user(request, f'🔄 {count} posts views reset to 0.')
    reset_views.short_description = "🔄 Reset view counts"
    
    # Кастомные CSS и JS
    class Media:
        css = {
            'all': ('admin/css/blog_admin.css',)
        }
        js = ('admin/js/blog_admin.js',)


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    """Админка для комментариев"""
    list_display = ('name', 'get_post_title', 'approval_status', 'created_at', 'comment_preview')
    list_filter = ('is_approved', 'created_at', 'post__category')
    search_fields = ('name', 'email', 'content', 'post__translations__title')
    readonly_fields = ('created_at', 'updated_at', 'comment_preview_full')
    actions = ['approve_comments', 'disapprove_comments', 'delete_spam']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Comment Info', {
            'fields': ('post', 'name', 'email', 'comment_preview_full')
        }),
        ('Content & Approval', {
            'fields': ('content', 'is_approved'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_post_title(self, obj):
        """Заголовок поста"""
        title = obj.post.safe_translation_getter('title', any_language=True)
        if title:
            return format_html(
                '<a href="{}" title="Edit post">{}</a>',
                reverse('admin:blog_blogpost_change', args=[obj.post.pk]),
                title[:50] + '...' if len(title) > 50 else title
            )
        return 'No title'
    get_post_title.short_description = 'Post'
    
    def approval_status(self, obj):
        """Статус одобрения"""
        if obj.is_approved:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✅ Approved</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">❌ Pending</span>'
        )
    approval_status.short_description = 'Status'
    approval_status.admin_order_field = 'is_approved'
    
    def comment_preview(self, obj):
        """Превью комментария"""
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return format_html('<span title="{}">{}</span>', obj.content, preview)
    comment_preview.short_description = 'Preview'
    
    def comment_preview_full(self, obj):
        """Полный превью комментария"""
        return format_html(
            '<div style="border: 1px solid #ddd; padding: 10px; border-radius: 4px; '
            'background: #f9f9f9; max-height: 200px; overflow-y: auto;">{}</div>',
            obj.content.replace('\n', '<br>')
        )
    comment_preview_full.short_description = 'Full Comment'
    
    def approve_comments(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'✅ {count} comments approved.')
    approve_comments.short_description = "✅ Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'❌ {count} comments disapproved.')
    disapprove_comments.short_description = "❌ Disapprove selected comments"
    
    def delete_spam(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'🗑️ {count} spam comments deleted.')
    delete_spam.short_description = "🗑️ Delete as spam"


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    """Админка для изображений блога"""
    list_display = ('get_post_title', 'image_preview', 'alt_text', 'created_at')
    list_filter = ('created_at', 'post__category')
    search_fields = ('alt_text', 'caption', 'post__translations__title')
    readonly_fields = ('created_at', 'image_preview_large')
    
    fieldsets = (
        (None, {
            'fields': ('post', 'image', 'image_preview_large')
        }),
        ('Image Details', {
            'fields': ('alt_text', 'caption'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_post_title(self, obj):
        title = obj.post.safe_translation_getter('title', any_language=True)
        return title[:50] + '...' if len(title) > 50 else title if title else 'No title'
    get_post_title.short_description = 'Post'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; '
                'border-radius: 4px;" />',
                obj.image.url
            )
        return 'No image'
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; '
                'border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return 'No image'
    image_preview_large.short_description = 'Large Preview'


# Настройка заголовков админки
admin.site.site_header = "🌍 Abroads Tours - Blog Administration"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Welcome to Blog Administration Panel"
