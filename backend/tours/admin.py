# backend/tours/admin.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
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
from .models import (
    Tour, TourCategory, TourDifficulty, TourImage, 
    TourFAQ, TourReview, TourMeetingPoint, BookingCode
)
import json


class WordPressStyleTourAdminMixin:
    """Миксин для WordPress стиля в управлении турами"""
    
    def get_wordpress_badge(self, text, color='blue', icon=''):
        """Создает WordPress-стиль badge"""
        colors = {
            'blue': '#0073aa',
            'green': '#46b450', 
            'red': '#dc3232',
            'orange': '#f56e28',
            'gray': '#82878c',
            'yellow': '#ffb900',
            'purple': '#826eb4',
            'teal': '#00a0d2'
        }
        return format_html(
            '<span class="wp-tour-badge" style="background: {}; color: white; '
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
            'warning': 'background: #f56e28; color: white; border: 1px solid #e65100;',
            'purple': 'background: #826eb4; color: white; border: 1px solid #6c5b7b;'
        }
        target_attr = f'target="{target}"' if target else ''
        
        return format_html(
            '<a href="{}" {} class="wp-tour-button" style="{} '
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
            'gray': '#82878c',
            'purple': '#826eb4',
            'teal': '#00a0d2'
        }
        return format_html(
            '<div class="wp-tour-stat-card" style="text-align: center; padding: 15px; '
            'background: white; border-radius: 4px; border-left: 4px solid {}; '
            'box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-width: 120px;">'
            '<div style="font-size: 24px; font-weight: bold; color: {}; margin-bottom: 5px;">{}</div>'
            '<div style="font-size: 12px; color: #666; text-transform: uppercase; '
            'letter-spacing: 0.5px;">{} {}</div>'
            '</div>',
            colors.get(color, color), colors.get(color, color), number, icon, label
        )


# Inline админки
class TourImageInline(admin.TabularInline, WordPressStyleTourAdminMixin):
    """WordPress-стиль inline для изображений тура"""
    model = TourImage
    extra = 1
    fields = ('image_thumbnail', 'image', 'alt_text', 'caption', 'sort_order', 'is_featured', 'image_actions')
    readonly_fields = ('image_thumbnail', 'image_actions')
    classes = ['wp-tour-inline']
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<div class="wp-tour-media-thumbnail" style="position: relative;">'
                '<img src="{}" style="width: 80px; height: 60px; '
                'object-fit: cover; border-radius: 4px; border: 2px solid #ddd; '
                'transition: all 0.2s ease;" '
                'onmouseover="this.style.borderColor=\'#0073aa\'; this.style.transform=\'scale(1.05)\';"'
                'onmouseout="this.style.borderColor=\'#ddd\'; this.style.transform=\'scale(1)\';" />'
                '<div style="position: absolute; top: 2px; right: 2px; '
                'background: rgba(0,0,0,0.7); color: white; border-radius: 2px; '
                'padding: 1px 4px; font-size: 9px;">🖼️</div>'
                '{}'
                '</div>',
                obj.image.url,
                '<div style="position: absolute; bottom: 2px; left: 2px; right: 2px; '
                'background: linear-gradient(transparent, rgba(0,115,170,0.9)); '
                'color: white; font-size: 8px; padding: 2px; text-align: center; '
                'border-radius: 0 0 4px 4px; font-weight: bold;">FEATURED</div>' if obj.is_featured else ''
            )
        return format_html(
            '<div class="wp-tour-media-placeholder" style="width: 80px; height: 60px; '
            'background: linear-gradient(135deg, #f1f1f1, #e1e1e1); '
            'border-radius: 4px; display: flex; align-items: center; '
            'justify-content: center; border: 2px dashed #ddd; color: #666;">'
            '<span style="font-size: 24px;">🖼️</span>'
            '</div>'
        )
    image_thumbnail.short_description = 'Preview'
    
    def image_actions(self, obj):
        if obj.pk:
            return format_html(
                '<div class="wp-tour-media-actions" style="display: flex; gap: 4px;">'
                '{} {}'
                '</div>',
                self.get_wordpress_button('Edit', f'/admin/tours/tourimage/{obj.pk}/change/', 'secondary', '✏️'),
                self.get_wordpress_button('Del', f'/admin/tours/tourimage/{obj.pk}/delete/', 'danger', '🗑️')
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    image_actions.short_description = 'Actions'


class TourFAQInline(admin.TabularInline, WordPressStyleTourAdminMixin):
    """WordPress-стиль inline для FAQ"""
    model = TourFAQ
    extra = 1
    fields = ('question_preview', 'sort_order', 'is_active', 'faq_actions')
    readonly_fields = ('question_preview', 'faq_actions')
    classes = ['wp-tour-inline', 'wp-tour-faq']
    
    def question_preview(self, obj):
        question = obj.safe_translation_getter('question', any_language=True) or 'No question'
        answer = obj.safe_translation_getter('answer', any_language=True) or 'No answer'
        
        return format_html(
            '<div class="wp-tour-faq-preview" style="max-width: 400px;">'
            '<div style="font-weight: bold; color: #0073aa; margin-bottom: 5px; font-size: 13px;">'
            '❓ {}</div>'
            '<div style="color: #666; font-size: 12px; line-height: 1.4;">{}</div>'
            '</div>',
            question[:80] + '...' if len(question) > 80 else question,
            answer[:120] + '...' if len(answer) > 120 else answer
        )
    question_preview.short_description = 'Question & Answer'
    
    def faq_actions(self, obj):
        if obj.pk:
            return format_html(
                '<div class="wp-tour-faq-actions" style="display: flex; gap: 4px;">'
                '{} {}'
                '</div>',
                self.get_wordpress_button('Edit', f'/admin/tours/tourfaq/{obj.pk}/change/', 'secondary', '✏️'),
                self.get_wordpress_button('Del', f'/admin/tours/tourfaq/{obj.pk}/delete/', 'danger', '🗑️')
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    faq_actions.short_description = 'Actions'


class TourMeetingPointInline(admin.TabularInline, WordPressStyleTourAdminMixin):
    """Inline для точек встречи"""
    model = TourMeetingPoint
    extra = 1
    fields = ('meeting_point_info', 'meeting_time', 'sort_order', 'is_primary')
    readonly_fields = ('meeting_point_info',)
    
    def meeting_point_info(self, obj):
        name = obj.safe_translation_getter('name', any_language=True) or 'No name'
        address = obj.safe_translation_getter('address', any_language=True) or 'No address'
        
        return format_html(
            '<div>'
            '<strong style="color: #0073aa;">📍 {}</strong><br>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            name[:50] + '...' if len(name) > 50 else name,
            address[:80] + '...' if len(address) > 80 else address
        )
    meeting_point_info.short_description = 'Meeting Point Info'


@admin.register(TourCategory)
class TourCategoryAdmin(TranslatableAdmin, WordPressStyleTourAdminMixin):
    """WordPress-стиль админка для категорий туров"""
    list_display = (
        'category_icon_display', 'get_name_styled', 'get_slug_styled', 
        'tour_statistics', 'status_toggle', 'category_actions'
    )
    list_filter = ('is_active',)
    search_fields = ('translations__name', 'translations__description')
    list_per_page = 20
    
    fieldsets = (
        ('🏷️ Category Information', {
            'fields': ('name', 'slug', 'description'),
            'classes': ('wp-tour-box', 'wp-tour-box-primary'),
        }),
        ('🎨 Display Settings', {
            'fields': ('icon', 'sort_order', 'is_active'),
            'classes': ('wp-tour-box', 'wp-tour-box-secondary'),
        }),
        ('📊 Statistics', {
            'fields': ('category_stats_display',),
            'classes': ('wp-tour-box', 'wp-tour-box-analytics'),
        }),
    )
    
    readonly_fields = ('category_stats_display',)
    
    def category_icon_display(self, obj):
        return format_html(
            '<div class="wp-tour-category-icon" style="font-size: 24px; text-align: center; '
            'background: linear-gradient(135deg, #0073aa, #00a0d2); '
            'color: white; width: 40px; height: 40px; border-radius: 8px; '
            'display: flex; align-items: center; justify-content: center; '
            'box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
            '<i class="{}"></i></div>',
            obj.icon or 'icon-mountain'
        )
    category_icon_display.short_description = ''
    
    def get_name_styled(self, obj):
        name = obj.safe_translation_getter('name', any_language=True) or f'Category {obj.pk}'
        tour_count = obj.tour_set.count()
        
        return format_html(
            '<div class="wp-tour-category-name" style="display: flex; flex-direction: column;">'
            '<div style="font-weight: bold; color: #0073aa; font-size: 14px; '
            'margin-bottom: 2px;">{}</div>'
            '<div style="font-size: 11px; color: #666;">{} tour{}</div>'
            '</div>',
            name, tour_count, 's' if tour_count != 1 else ''
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
                '<span style="color: #999;">../tours/</span>{}'
                '</div>',
                slug
            )
        return format_html(
            '<span style="color: #dc3232; font-style: italic; font-size: 11px;">⚠️ No slug</span>'
        )
    get_slug_styled.short_description = 'URL Slug'
    
    def tour_statistics(self, obj):
        published = obj.tour_set.filter(status='published').count()
        draft = obj.tour_set.filter(status='draft').count()
        total = obj.tour_set.count()
        
        if published > 3:
            main_color, performance = '#46b450', 'Active'
        elif published > 0:
            main_color, performance = '#f56e28', 'Medium'
        else:
            main_color, performance = '#82878c', 'Low'
        
        return format_html(
            '<div class="wp-tour-stats" style="text-align: center; '
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
            'text-transform: uppercase;">{} Level</div>'
            '</div>',
            main_color, published, draft, main_color, performance
        )
    tour_statistics.short_description = 'Tours'
    
    def status_toggle(self, obj):
        if obj.is_active:
            return format_html(
                '<div style="text-align: center;">'
                '{}'
                '<div style="font-size: 10px; color: #46b450; margin-top: 3px; '
                'font-weight: bold;">ACTIVE</div>'
                '</div>',
                self.get_wordpress_badge('Live', 'green', '✓')
            )
        return format_html(
            '<div style="text-align: center;">'
            '{}'
            '<div style="font-size: 10px; color: #82878c; margin-top: 3px; '
            'font-weight: bold;">HIDDEN</div>'
            '</div>',
            self.get_wordpress_badge('Hidden', 'gray', '○')
        )
    status_toggle.short_description = 'Status'
    
    def category_actions(self, obj):
        if obj.pk:
            return format_html(
                '<div class="wp-tour-actions" style="display: flex; flex-direction: column; gap: 4px;">'
                '{}'
                '{}'
                '{}'
                '</div>',
                self.get_wordpress_button('Edit', f'/admin/tours/tourcategory/{obj.pk}/change/', 'primary', '✏️'),
                self.get_wordpress_button('Tours', f'/admin/tours/tour/?category__id__exact={obj.pk}', 'secondary', '🎯'),
                self.get_wordpress_button('View', obj.get_absolute_url(), 'secondary', '👁️', '_blank') if obj.get_absolute_url() != '#' else ''
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    category_actions.short_description = 'Actions'
    
    def category_stats_display(self, obj):
        if not obj.pk:
            return format_html('<p style="color: #999;">Save category to see statistics</p>')
        
        total_tours = obj.tour_set.count()
        published_tours = obj.tour_set.filter(status='published').count()
        draft_tours = obj.tour_set.filter(status='draft').count()
        featured_tours = obj.tour_set.filter(is_featured=True).count()
        total_views = sum(tour.views_count for tour in obj.tour_set.all())
        
        return format_html(
            '<div class="wp-tour-category-stats" style="background: #f9f9f9; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 15px 0; color: #0073aa;">🎯 Category Analytics</h4>'
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px;">'
            '{}'
            '{}'
            '{}'
            '{}'
            '{}'
            '</div>'
            '</div>',
            self.get_wordpress_stat_card(total_tours, 'Total Tours', 'blue', '🎯'),
            self.get_wordpress_stat_card(published_tours, 'Published', 'green', '✅'),
            self.get_wordpress_stat_card(draft_tours, 'Drafts', 'gray', '📝'),
            self.get_wordpress_stat_card(featured_tours, 'Featured', 'purple', '⭐'),
            self.get_wordpress_stat_card(total_views, 'Total Views', 'teal', '👁️')
        )
    category_stats_display.short_description = 'Detailed Statistics'


@admin.register(TourDifficulty)
class TourDifficultyAdmin(admin.ModelAdmin, WordPressStyleTourAdminMixin):
    """Админка для уровней сложности туров"""
    list_display = ('difficulty_icon', 'name', 'level_badge', 'tour_count', 'difficulty_actions')
    list_filter = ('level',)
    ordering = ('level',)
    
    def difficulty_icon(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; background: {}; color: white; '
            'border-radius: 50%; display: flex; align-items: center; justify-content: center; '
            'font-size: 14px; font-weight: bold;">{}</div>',
            obj.color, obj.level
        )
    difficulty_icon.short_description = 'Level'
    
    def level_badge(self, obj):
        colors = ['green', 'blue', 'orange', 'red', 'red']
        color = colors[min(obj.level - 1, 4)] if obj.level <= 5 else 'red'
        return self.get_wordpress_badge(f'Level {obj.level}', color)
    level_badge.short_description = 'Difficulty'
    
    def tour_count(self, obj):
        count = obj.tour_set.count()
        return format_html(
            '<span style="font-weight: bold; color: #0073aa;">{} tour{}</span>',
            count, 's' if count != 1 else ''
        )
    tour_count.short_description = 'Tours'
    
    def difficulty_actions(self, obj):
        if obj.pk:
            return format_html(
                '<div style="display: flex; gap: 4px;">'
                '{} {}'
                '</div>',
                self.get_wordpress_button('Edit', f'/admin/tours/tourdifficulty/{obj.pk}/change/', 'secondary', '✏️'),
                self.get_wordpress_button('Tours', f'/admin/tours/tour/?difficulty__id__exact={obj.pk}', 'primary', '🎯')
            )
        return '-'
    difficulty_actions.short_description = 'Actions'


@admin.register(Tour)
class TourAdmin(TranslatableAdmin, WordPressStyleTourAdminMixin):
    """Главная админка для туров в WordPress стиле"""
    
    list_display = (
        'tour_thumbnail', 'get_title_with_status', 'category_info', 
        'pricing_display', 'performance_score', 'tour_actions'
    )
    list_filter = (
        'status', 'category', 'difficulty', 'tour_type', 
        'is_featured', 'free_cancellation'
    )
    search_fields = (
        'translations__title', 'translations__short_description', 
        'author__username', 'category__translations__name'
    )
    list_per_page = 25
    ordering = ['-is_featured', 'sort_order', '-created_at']
    
    # Inline админки
    inlines = [TourImageInline, TourFAQInline, TourMeetingPointInline]
    
    # Fieldsets для формы редактирования
    fieldsets = (
        ('🎯 Tour Basics', {
            'fields': (
                'author', 'category', 'difficulty', 'status', 'tour_type', 
                'is_featured', 'sort_order'
            ),
            'classes': ('wp-tour-box', 'wp-tour-box-primary'),
        }),
        ('📝 Content', {
            'fields': (
                'title', 'slug', 'short_description', 'featured_image'
            ),
            'classes': ('wp-tour-box', 'wp-tour-box-content'),
        }),
        ('📖 Detailed Content', {
            'fields': (
                'tour_highlights', 'why_unique', 'what_experience',
                'whats_included', 'whats_not_included'
            ),
            'classes': ('wp-tour-box', 'wp-tour-box-detailed'),
        }),
        ('⏰ Tour Details', {
            'fields': (
                'duration_hours', 'duration_minutes', 'max_group_size', 
                'languages', 'free_cancellation', 'reserve_now_pay_later', 
                'instant_confirmation'
            ),
            'classes': ('wp-tour-box', 'wp-tour-box-details'),
        }),
        ('💰 Pricing', {
            'fields': ('price_adult', 'price_child', 'price_private'),
            'classes': ('wp-tour-box', 'wp-tour-box-pricing'),
        }),
        ('⭐ Rating & Reviews', {
            'fields': ('rating', 'reviews_count'),
            'classes': ('wp-tour-box', 'wp-tour-box-rating'),
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'tags'),
            'classes': ('wp-tour-box', 'wp-tour-box-seo', 'collapse'),
        }),
        ('📊 Analytics', {
            'fields': ('tour_analytics_dashboard',),
            'classes': ('wp-tour-box', 'wp-tour-box-analytics'),
        }),
        ('👁️ Preview', {
            'fields': ('tour_preview_card',),
            'classes': ('wp-tour-box', 'wp-tour-box-preview'),
        }),
    )
    
    readonly_fields = ('tour_analytics_dashboard', 'tour_preview_card')
    
    # Методы для list_display
    def tour_thumbnail(self, obj):
        """Миниатюра тура"""
        if obj.featured_image:
            return format_html(
                '<div class="wp-tour-thumbnail" style="position: relative; width: 60px; height: 60px;">'
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; '
                'border-radius: 8px; border: 2px solid {};" />'
                '{}'
                '</div>',
                obj.featured_image.url,
                '#46b450' if obj.status == 'published' else '#82878c',
                '<div style="position: absolute; top: 2px; right: 2px; '
                'background: rgba(0,0,0,0.8); color: white; border-radius: 2px; '
                'padding: 1px 3px; font-size: 8px; font-weight: bold;">⭐</div>' if obj.is_featured else ''
            )
        return format_html(
            '<div style="width: 60px; height: 60px; background: linear-gradient(135deg, #f1f1f1, #e1e1e1); '
            'border-radius: 8px; display: flex; align-items: center; justify-content: center; '
            'border: 2px solid #ddd; color: #999; font-size: 20px;">🎯</div>'
        )
    tour_thumbnail.short_description = ''
    
    def get_title_with_status(self, obj):
        """Название тура со статусом"""
        title = obj.safe_translation_getter('title', any_language=True) or f'Tour {obj.pk}'
        
        status_colors = {
            'published': '#46b450',
            'draft': '#f56e28', 
            'archived': '#82878c'
        }
        
        status_icons = {
            'published': '🟢',
            'draft': '🟡',
            'archived': '⚫'
        }
        
        return format_html(
            '<div class="wp-tour-title-status">'
            '<div style="font-weight: bold; color: #0073aa; font-size: 14px; margin-bottom: 3px; '
            'max-width: 250px; line-height: 1.3;">{}</div>'
            '<div style="display: flex; align-items: center; gap: 5px;">'
            '<span style="font-size: 10px;">{}</span>'
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 10px; font-size: 9px; font-weight: bold; '
            'text-transform: uppercase;">{}</span>'
            '{}'
            '</div>'
            '</div>',
            title,
            status_icons.get(obj.status, '🔘'),
            status_colors.get(obj.status, '#82878c'),
            obj.status,
            '<span style="background: #826eb4; color: white; padding: 2px 6px; '
            'border-radius: 10px; font-size: 8px; font-weight: bold; '
            'margin-left: 5px;">FEATURED</span>' if obj.is_featured else ''
        )
    get_title_with_status.short_description = 'Tour Title & Status'
    get_title_with_status.admin_order_field = 'translations__title'
    
    def category_info(self, obj):
        """Информация о категории и типе"""
        category_name = obj.category.safe_translation_getter('name', any_language=True) if obj.category else 'No Category'
        tour_type = obj.get_tour_type_display()
        
        return format_html(
            '<div class="wp-tour-category-info" style="text-align: center;">'
            '<div style="font-weight: bold; color: #0073aa; font-size: 12px;">{}</div>'
            '<div style="font-size: 10px; color: #666;">{}</div>'
            '</div>',
            category_name, tour_type
        )
    category_info.short_description = 'Category & Type'
    
    def pricing_display(self, obj):
        """Отображение цен"""
        return format_html(
            '<div class="wp-tour-pricing" style="text-align: center; '
            'background: linear-gradient(135deg, #f9f9f9, #f1f1f1); '
            'padding: 8px; border-radius: 6px; border: 1px solid #e1e1e1;">'
            '<div style="font-size: 18px; font-weight: bold; color: #46b450; margin-bottom: 3px;">'
            '€{}</div>'
            '<div style="font-size: 10px; color: #666;">ADULT</div>'
            '{}'
            '</div>',
            obj.price_adult,
            f'<div style="font-size: 11px; color: #0073aa; margin-top: 2px;">Child: €{obj.price_child}</div>' 
            if obj.price_child else ''
        )
    pricing_display.short_description = 'Pricing'
    
    def performance_score(self, obj):
        """Performance Score как общая оценка тура"""
        score = 0
        issues = []
        
        # Проверяем заполненность контента
        if obj.safe_translation_getter('tour_highlights', any_language=True):
            score += 15
        else:
            issues.append('No highlights')
            
        if obj.safe_translation_getter('why_unique', any_language=True):
            score += 15
        else:
            issues.append('Why unique missing')
            
        if obj.safe_translation_getter('what_experience', any_language=True):
            score += 15
        else:
            issues.append('Experience missing')
            
        if obj.featured_image:
            score += 10
        else:
            issues.append('No featured image')
            
        if obj.images.count() >= 4:
            score += 10
        else:
            issues.append(f'Only {obj.images.count()}/4 images')
            
        if obj.faqs.count() >= 3:
            score += 15
        else:
            issues.append(f'Only {obj.faqs.count()}/3 FAQs')
            
        # Бонусы
        if obj.booking_count > 0:
            score += 10
        if obj.views_count > 100:
            score += 10
        
        # Определяем цвет и статус
        if score >= 80:
            color, status, icon = '#46b450', 'Excellent', '🟢'
        elif score >= 60:
            color, status, icon = '#0073aa', 'Good', '🔵'
        elif score >= 40:
            color, status, icon = '#f56e28', 'Needs Work', '🟡'
        else:
            color, status, icon = '#dc3232', 'Poor', '🔴'
        
        return format_html(
            '<div class="wp-tour-performance" style="text-align: center; '
            'background: linear-gradient(135deg, #fff, #f9f9f9); '
            'padding: 10px; border-radius: 6px; border: 1px solid #e1e1e1;">'
            '<div style="font-size: 18px; font-weight: bold; color: {}; margin-bottom: 4px;">'
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
    performance_score.short_description = 'Quality'
    
    def tour_actions(self, obj):
        """Действия для тура"""
        if obj.pk:
            actions = []
            
            # Edit button
            actions.append(
                self.get_wordpress_button('Edit', f'/admin/tours/tour/{obj.pk}/change/', 'primary', '✏️')
            )
            
            # View button (если опубликован)
            if obj.status == 'published':
                actions.append(
                    self.get_wordpress_button('View', obj.get_absolute_url(), 'secondary', '👁️', '_blank')
                )
            
            # Quick publish/unpublish
            if obj.status != 'published':
                actions.append(
                    self.get_wordpress_button('Publish', f'#', 'success', '🚀')
                )
            else:
                actions.append(
                    self.get_wordpress_button('Draft', f'#', 'warning', '📝')
                )
            
            # Duplicate button
            actions.append(
                self.get_wordpress_button('Copy', f'#', 'secondary', '📄')
            )
            
            return format_html(
                '<div class="wp-tour-actions" style="display: flex; flex-direction: column; gap: 3px;">'
                '{}'
                '</div>',
                ''.join(actions)
            )
        return format_html('<span style="color: #999; font-size: 11px;">Save first</span>')
    tour_actions.short_description = 'Actions'
    
    # Readonly поля
    def tour_preview_card(self, obj):
        """Карточка предпросмотра тура"""
        if not obj.pk:
            return format_html('<p style="color: #999;">Save tour to see preview</p>')
        
        title = obj.safe_translation_getter('title', any_language=True) or 'No title'
        description = obj.safe_translation_getter('short_description', any_language=True) or 'No description'
        
        return format_html(
            '<div class="wp-tour-preview" style="background: white; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
            '<div style="display: flex; gap: 15px;">'
            '{}'
            '<div style="flex: 1;">'
            '<h3 style="margin: 0 0 10px 0; color: #0073aa; font-size: 18px; line-height: 1.3;">{}</h3>'
            '<p style="color: #666; font-size: 14px; line-height: 1.5; margin: 0 0 10px 0;">{}</p>'
            '<div style="display: flex; gap: 10px; align-items: center;">'
            '<span style="font-size: 18px; font-weight: bold; color: #46b450;">€{}</span>'
            '<span style="font-size: 12px; color: #666;">• {} • Max {} people</span>'
            '</div>'
            '</div>'
            '</div>'
            '</div>',
            f'<img src="{obj.featured_image.url}" style="width: 150px; height: 100px; '
            f'object-fit: cover; border-radius: 4px;" />' if obj.featured_image else 
            '<div style="width: 150px; height: 100px; background: #f1f1f1; '
            'border-radius: 4px; display: flex; align-items: center; justify-content: center; '
            'color: #999; font-size: 24px;">🎯</div>',
            title,
            description,
            obj.price_adult,
            obj.get_duration_display(),
            obj.max_group_size
        )
    tour_preview_card.short_description = 'Tour Preview'
    
    def tour_analytics_dashboard(self, obj):
        """Аналитическая панель"""
        if not obj.pk:
            return format_html('<p style="color: #999;">Save tour to see analytics</p>')
        
        return format_html(
            '<div class="wp-tour-analytics" style="background: #f9f9f9; padding: 20px; '
            'border-radius: 8px; border: 1px solid #e1e1e1;">'
            '<h4 style="margin: 0 0 20px 0; color: #0073aa;">🎯 Tour Analytics Dashboard</h4>'
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); '
            'gap: 15px;">'
            '{}'
            '{}'
            '{}'
            '{}'
            '{}'
            '{}'
            '</div>'
            '</div>',
            self.get_wordpress_stat_card(obj.views_count, 'Page Views', 'blue', '👁️'),
            self.get_wordpress_stat_card(obj.booking_count, 'Bookings', 'green', '📋'),
            self.get_wordpress_stat_card(obj.images.count(), 'Images', 'orange', '🖼️'),
            self.get_wordpress_stat_card(obj.faqs.count(), 'FAQs', 'purple', '❓'),
            self.get_wordpress_stat_card(obj.reviews.count(), 'Reviews', 'teal', '⭐'),
            self.get_wordpress_stat_card(f'{obj.rating:.1f}', 'Rating', 'yellow', '⭐')
        )
    tour_analytics_dashboard.short_description = 'Analytics Dashboard'
    
    # Действия
    actions = ['publish_tours', 'draft_tours', 'feature_tours', 'duplicate_tours']
    
    def publish_tours(self, request, queryset):
        count = queryset.update(status='published')
        messages.success(request, f'🚀 {count} tour{"s" if count != 1 else ""} published!')
    publish_tours.short_description = "🚀 Publish selected tours"
    
    def draft_tours(self, request, queryset):
        count = queryset.update(status='draft')
        messages.warning(request, f'📝 {count} tour{"s" if count != 1 else ""} moved to draft.')
    draft_tours.short_description = "📝 Move to draft"
    
    def feature_tours(self, request, queryset):
        count = queryset.update(is_featured=True)
        messages.success(request, f'⭐ {count} tour{"s" if count != 1 else ""} marked as featured!')
    feature_tours.short_description = "⭐ Mark as featured"
    
    def duplicate_tours(self, request, queryset):
        duplicated = 0
        for tour in queryset:
            tour.pk = None
            tour.slug = None
            tour.status = 'draft'
            tour.save()
            duplicated += 1
        messages.success(request, f'📄 {duplicated} tour{"s" if duplicated != 1 else ""} duplicated!')
    duplicate_tours.short_description = "📄 Duplicate selected tours"


# Остальные админ-классы
@admin.register(TourImage)
class TourImageAdmin(admin.ModelAdmin, WordPressStyleTourAdminMixin):
    list_display = ('image_thumbnail', 'tour_info', 'alt_text', 'sort_order', 'is_featured')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('tour__translations__title', 'alt_text', 'caption')
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '—'
    image_thumbnail.short_description = 'Image'
    
    def tour_info(self, obj):
        tour_title = obj.tour.safe_translation_getter('title', any_language=True)
        return format_html(
            '<a href="/admin/tours/tour/{}/change/" style="color: #0073aa;">{}</a>',
            obj.tour.pk, tour_title or f'Tour {obj.tour.pk}'
        )
    tour_info.short_description = 'Tour'


@admin.register(TourFAQ)
class TourFAQAdmin(TranslatableAdmin, WordPressStyleTourAdminMixin):
    list_display = ('question_preview', 'tour_link', 'sort_order', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('tour__translations__title', 'translations__question')
    
    def question_preview(self, obj):
        question = obj.safe_translation_getter('question', any_language=True) or 'No question'
        return question[:50] + '...' if len(question) > 50 else question
    question_preview.short_description = 'Question'
    
    def tour_link(self, obj):
        tour_title = obj.tour.safe_translation_getter('title', any_language=True)
        return format_html(
            '<a href="/admin/tours/tour/{}/change/">{}</a>',
            obj.tour.pk, tour_title or f'Tour {obj.tour.pk}'
        )
    tour_link.short_description = 'Tour'


@admin.register(TourReview)
class TourReviewAdmin(TranslatableAdmin, WordPressStyleTourAdminMixin):
    list_display = ('author_name', 'tour_link', 'rating_stars', 'review_date', 'is_featured', 'is_verified')
    list_filter = ('rating', 'is_featured', 'is_verified', 'review_date')
    search_fields = ('author_name', 'tour__translations__title', 'translations__title')
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="font-size: 16px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    def tour_link(self, obj):
        tour_title = obj.tour.safe_translation_getter('title', any_language=True)
        return format_html(
            '<a href="/admin/tours/tour/{}/change/">{}</a>',
            obj.tour.pk, tour_title or f'Tour {obj.tour.pk}'
        )
    tour_link.short_description = 'Tour'


@admin.register(TourMeetingPoint)
class TourMeetingPointAdmin(TranslatableAdmin, WordPressStyleTourAdminMixin):
    list_display = ('meeting_point_name', 'tour_link', 'meeting_time', 'is_primary', 'sort_order')
    list_filter = ('is_primary', 'meeting_time')
    search_fields = ('tour__translations__title', 'translations__name', 'translations__address')
    
    def meeting_point_name(self, obj):
        name = obj.safe_translation_getter('name', any_language=True) or 'No name'
        return name[:50] + '...' if len(name) > 50 else name
    meeting_point_name.short_description = 'Meeting Point'
    
    def tour_link(self, obj):
        tour_title = obj.tour.safe_translation_getter('title', any_language=True)
        return format_html(
            '<a href="/admin/tours/tour/{}/change/">{}</a>',
            obj.tour.pk, tour_title or f'Tour {obj.tour.pk}'
        )
    tour_link.short_description = 'Tour'


@admin.register(BookingCode)
class BookingCodeAdmin(admin.ModelAdmin, WordPressStyleTourAdminMixin):
    list_display = ('tour_link', 'booking_system', 'is_active', 'updated_at')
    list_filter = ('booking_system', 'is_active')
    search_fields = ('tour__translations__title',)
    
    def tour_link(self, obj):
        tour_title = obj.tour.safe_translation_getter('title', any_language=True)
        return format_html(
            '<a href="/admin/tours/tour/{}/change/">{}</a>',
            obj.tour.pk, tour_title or f'Tour {obj.tour.pk}'
        )
    tour_link.short_description = 'Tour'


# Настройки админки
admin.site.site_header = "🎯 Abroads Tours - Complete CMS"
admin.site.site_title = "Tours & Blog CMS"
admin.site.index_title = "Welcome to Complete Tours & Blog Administration"
