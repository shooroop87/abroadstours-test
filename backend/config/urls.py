# backend/config/urls.py - ОТЛАДОЧНАЯ ВЕРСИЯ
from django.contrib import admin
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse, FileResponse, Http404
from django.urls import include, path, re_path
from django.views.decorators.http import require_GET
from django.views.i18n import set_language
import os

# Импорты из core приложения
from core.sitemaps import CompleteSitemap
from core.views import subscribe_to_newsletter

# Импорты для блога (если sitemaps и feeds уже созданы)
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

# Прямая функция для обслуживания медиа
def serve_media_debug(request, path):
    """Отладочное обслуживание медиа-файлов"""
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    print(f"🐛 MEDIA REQUEST: {request.method} {path}")
    print(f"🐛 FULL PATH: {file_path}")
    print(f"🐛 EXISTS: {os.path.exists(file_path)}")
    print(f"🐛 IS FILE: {os.path.isfile(file_path) if os.path.exists(file_path) else 'N/A'}")
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        print(f"🐛 SERVING FILE: {file_path}")
        try:
            response = FileResponse(open(file_path, 'rb'))
            print(f"🐛 RESPONSE CREATED: {response}")
            return response
        except Exception as e:
            print(f"🐛 ERROR SERVING FILE: {e}")
            raise Http404(f"Ошибка обслуживания файла: {e}")
    else:
        print(f"🐛 FILE NOT FOUND: {file_path}")
        # Показываем содержимое директории для отладки
        dir_path = os.path.dirname(file_path)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"🐛 DIR CONTENTS: {files}")
        raise Http404("Медиа файл не найден")

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
    # ПЕРВЫМ делом - медиа файлы (КРИТИЧЕСКИ ВАЖНО!)
    re_path(r'^media/(?P<path>.*)$', serve_media_debug, name='debug_media'),
    
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("set-language/", set_language, name="set_language"),
    path("subscribe/", subscribe_to_newsletter, name="subscribe"),
    
    # Django admin
    path("admin/", admin.site.urls),
    
    # CKEditor
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

# Добавляем RSS feeds для блога если доступны
if BLOG_AVAILABLE:
    urlpatterns.extend([
        path("blog/feed/", BlogFeed(), name="blog_feed"),
        path("blog/feed/atom/", AtomBlogFeed(), name="blog_feed_atom"),
    ])

# --- Языковые маршруты ---
urlpatterns += i18n_patterns(
    # Blog приложение - обрабатывается первым для /blog/ URL-ов
    path("blog/", include("blog.urls")),
    
    # Core приложение - все остальные URL-ы включая главную страницу
    path("", include("core.urls")),
    
    prefix_default_language=False,
)

# === ДОПОЛНИТЕЛЬНО В DEBUG РЕЖИМЕ ===
if settings.DEBUG:
    print("🐛 DEBUG: Добавляем django_browser_reload...")
    
    # Django browser reload (если используется)
    if 'django_browser_reload' in settings.INSTALLED_APPS:
        urlpatterns += [
            path("__reload__/", include("django_browser_reload.urls")),
        ]
    
    # ДОПОЛНИТЕЛЬНО: static файлы
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

print(f"🐛 DEBUG: Итого URL patterns: {len(urlpatterns)}")
print("🐛 DEBUG: Медиа файлы обслуживаются через serve_media_debug")

# Обработчики ошибок (в core приложении)
handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"
