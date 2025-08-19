# backend/config/urls.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
from django.contrib import admin
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.decorators.http import require_GET
from django.views.i18n import set_language

# Импорты из core приложения
from core.sitemaps import CompleteSitemap
from core.views import subscribe_to_newsletter

# Импорты для блога
try:
    from blog.sitemaps import BlogPostSitemap, CategorySitemap
    from blog.feeds import BlogFeed, AtomBlogFeed
    BLOG_AVAILABLE = True
except ImportError:
    BLOG_AVAILABLE = False

# --- Sitemap config ---
sitemaps = {
    "complete": CompleteSitemap,
}

if BLOG_AVAILABLE:
    sitemaps.update({
        "blog_posts": BlogPostSitemap,
        "blog_categories": CategorySitemap,
    })

# --- robots.txt ---
@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    if BLOG_AVAILABLE:
        lines.extend([
            "",
            "# Blog RSS feeds",
            f"# RSS: https://{request.get_host()}/blog/feed/",
            f"# Atom: https://{request.get_host()}/blog/feed/atom/",
        ])
    return HttpResponse("\n".join(lines), content_type="text/plain")

# --- URLs без языкового префикса ---
urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("set-language/", set_language, name="set_language"),
    path("subscribe/", subscribe_to_newsletter, name="subscribe"),
    
    # Django admin
    path("admin/", admin.site.urls),
    
    # CKEditor
    path("ckeditor/", include("ckeditor_uploader.urls")),

    # Django-Filer маршруты
    path("filer/", include("filer.urls")),  
]

# Добавляем RSS feeds для блога если доступны
if BLOG_AVAILABLE:
    urlpatterns.extend([
        path("blog/feed/", BlogFeed(), name="blog_feed"),
        path("blog/feed/atom/", AtomBlogFeed(), name="blog_feed_atom"),
    ])

# --- Языковые маршруты ---
urlpatterns += i18n_patterns(
    # Tours приложение - обрабатывается первым для /tours/ URL-ов
    path("tours/", include("tours.urls")),
    
    # Blog приложение - обрабатывается первым для /blog/ URL-ов
    path("blog/", include("blog.urls")),
    
    # Core приложение - все остальные URL-ы включая главную страницу
    path("", include("core.urls")),
    
    prefix_default_language=False,
)

# === МЕДИА ФАЙЛЫ В DEBUG РЕЖИМЕ ===
if settings.DEBUG:
    print("🐛 DEBUG: Настройка обслуживания медиа-файлов...")
    
    from django.conf.urls.static import static
    from django.views.static import serve
    
    # Статические файлы
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Django browser reload (если используется)
    if 'django_browser_reload' in settings.INSTALLED_APPS:
        urlpatterns += [
            path("__reload__/", include("django_browser_reload.urls")),
        ]

print(f"🐛 DEBUG: Итого URL patterns: {len(urlpatterns)}")
print(f"🐛 DEBUG: MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"🐛 DEBUG: MEDIA_URL: {settings.MEDIA_URL}")

# Обработчики ошибок
handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"
