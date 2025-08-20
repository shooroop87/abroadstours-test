import io
import os
import sys
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("SECRET_KEY", "1insecure1-1default1")

# DEBUG выключает все виды кэша и сжатия
DEBUG = True

# Или если хотите разрешить все хосты в DEBUG режиме:
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost 127.0.0.1").split()

CSRF_TRUSTED_ORIGINS = [
    "https://*.abroadstours.com",
    "https://abroadstours.com",
    "http://localhost",
    'http://localhost:8000',
    'http://backend-1:8000',
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
]

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Django-Filer и зависимости
    "easy_thumbnails",
    "filer",
    "mptt",
    # Ваши приложения
    "core",
    "blog",
    #"tours",
    # Остальные зависимости
    "parler",
    "ckeditor",
    "ckeditor_uploader",
    "taggit",
    "meta",
]

# Dev-only apps
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]

MIDDLEWARE = [
    # 1. GZip-сжатие (опционально, WhiteNoise уже сжимает статику)
    "django.middleware.gzip.GZipMiddleware",
    # 2. Безопасность
    "django.middleware.security.SecurityMiddleware",
    # 🔹 WhiteNoise — должен быть ЗДЕСЬ
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # 3. Сессии (нужны до LocaleMiddleware)
    "django.contrib.sessions.middleware.SessionMiddleware",
    # 4. Локализация
    "django.middleware.locale.LocaleMiddleware",
    # "core.middleware.StrictLanguageMiddleware",
    # 5. Общие заголовки и корректировка URL
    "django.middleware.common.CommonMiddleware",
    # 6. CSRF и аутентификация
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # 7. Защита от iframe
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "core.context_processors.default_schema",
                "blog.context_processors.blog_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "abroadtours"),
        "USER": os.getenv("POSTGRES_USER", "abroadtours_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", 5432),
    }
}

DEFAULT_CHARSET = "utf-8"
FILE_CHARSET = "utf-8"

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("fr", _("French")),
    ("de", _("German")),
    ("es", _("Spanish")),
    ("nl", _("Dutch")),
]

LOCALE_PATHS = [BASE_DIR / "core" / "locale"]

# Static & media
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
STATIC_ROOT = BASE_DIR / "collected_static"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Настройки Django-Filer
THUMBNAIL_HIGH_RESOLUTION = True
THUMBNAIL_QUALITY = 90
THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "easy_thumbnails.processors.scale_and_crop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # "PASSWORD": os.getenv("REDIS_PASSWORD"),  # если настроена авторизация
            },
        }
    }

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "your-smtp-server.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@domain.com"
EMAIL_HOST_PASSWORD = "your-password"
DEFAULT_FROM_EMAIL = "Abroads Tours <noreply@abroadstours.com>"
CONTACT_EMAIL = "abroadstour@gmail.com"

# Контакты
CONTACT_PHONE = "+39-339-2168555"
WHATSAPP_NUMBER = "393392168555"

# SendPulse
SENDPULSE_API_USER_ID = os.getenv("SENDPULSE_API_USER_ID", "your-user-id")
SENDPULSE_API_SECRET = os.getenv("SENDPULSE_API_SECRET", "your-secret")
SENDPULSE_ADDRESS_BOOK_ID = os.getenv("SENDPULSE_ADDRESS_BOOK_ID", "your-book-id")

# SEO / верификация
GOOGLE_ANALYTICS_ID = "GA_MEASUREMENT_ID"
YANDEX_METRICA_ID = "YOUR_YANDEX_ID"
BING_WEBMASTER_ID = "YOUR_BING_ID"
BING_UET_TAG = "YOUR_BING_UET_TAG"
GOOGLE_SITE_VERIFICATION = ""
YANDEX_VERIFICATION = ""
BING_SITE_VERIFICATION = ""

# hCaptcha
HCAPTCHA_SITEKEY = "your-site-key-here"
HCAPTCHA_SECRET = "your-secret-key-here"
HCAPTCHA_DEFAULT_CONFIG = {
    "theme": "light",
    "size": "normal",
}

# Misc
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# stdout fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Путь к логам (в рабочей директории /app)
LOGS_DIR = BASE_DIR / 'logs'

# Создаем директорию для логов если её нет
os.makedirs(LOGS_DIR, exist_ok=True)

# Настройки логирования (исправленные)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '🐛 {levelname} [{asctime}] {name} {module}:{lineno} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed'
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'debug.log',
            'formatter': 'detailed',
        },
        'media_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'media.log',
            'formatter': 'detailed',
        },
        'blog_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'blog.log',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'blog': {
            'handlers': ['blog_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'blog.models': {
            'handlers': ['blog_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.core.files': {
            'handlers': ['media_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'PIL': {
            'handlers': ['media_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ckeditor': {
            'handlers': ['media_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_debug', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['file_debug'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    }
}

# API ключи для отзывов
TRIPADVISOR_API_KEY = os.getenv("TRIPADVISOR_API_KEY", "")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
GOOGLE_PLACE_ID = os.getenv("GOOGLE_PLACE_ID", "")
REVIEWS_CACHE_TIMEOUT = int(os.getenv("REVIEWS_CACHE_TIMEOUT", 86400))

# Логирование отзывы
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "reviews_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/tmp/reviews.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "services.multi_reviews_service": {
            "handlers": ["reviews_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}


# Настройки Parler для переводов
PARLER_LANGUAGES = {
    None: (
        {'code': 'en'},
        {'code': 'fr'},
        {'code': 'de'},
        {'code': 'es'},
        {'code': 'nl'},
    ),
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,
    }
}

# CKEditor настройки
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_RESTRICT_BY_USER = False         # общий доступ к медиа как в WP
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'height': 400,
        'width': '100%',
        'toolbarGroups': [
            {'name': 'document', 'groups': ['mode', 'document', 'doctools']},
            {'name': 'clipboard', 'groups': ['clipboard', 'undo']},
            {'name': 'editing', 'groups': ['find', 'selection', 'spellchecker']},
            {'name': 'forms'},
            '/',
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup']},
            {'name': 'paragraph', 'groups': ['list', 'indent', 'blocks', 'align', 'bidi']},
            {'name': 'links'},
            {'name': 'insert'},
            '/',
            {'name': 'styles'},
            {'name': 'colors'},
            {'name': 'tools'},
            {'name': 'others'},
        ],
        'removePlugins': 'stylesheetparser',
        'extraPlugins': ','.join([
            'uploadimage',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
        'format_tags': 'p;h1;h2;h3;h4;h5;h6;pre;address;div',
        'contentsCss': ['/static/admin/css/ckeditor.css'],
    },
    'blog': {
        'toolbar': 'Custom',
        'height': 500,
        'width': '100%',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Image', 'Table'],
            ['Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
        ],
        'format_tags': 'p;h1;h2;h3;h4;h5;h6',
        'extraPlugins': 'uploadimage',
    },
    # Специальная конфигурация для полной ширины
    'fullwidth': {
        'toolbar': 'Full',
        'height': 400,
        'width': '100%',
        'resize_enabled': True,
        'resize_dir': 'vertical',
        'autoGrow_onStartup': True,
        'contentsCss': ['/static/admin/css/ckeditor.css'],
        'bodyClass': 'fullwidth-editor',
        'stylesSet': False,
    }
}

# Настройки для тегов
TAGGIT_CASE_INSENSITIVE = True

# Настройки миниатюр
THUMBNAIL_FORMAT = 'WEBP'
THUMBNAIL_QUALITY = 85
THUMBNAIL_PRESERVE_FORMAT = False

# Настройки для пагинации
PAGINATE_BY = 10

# Настройки для загрузки изображений
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 15 * 1024 * 1024  # 15MB

# Разрешенные форматы изображений
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# Пилау для обработки изображений
IMAGE_QUALITY = 85
MAX_IMAGE_WIDTH = 1200
MAX_IMAGE_HEIGHT = 1200

# Настройки easy-thumbnails для blog
THUMBNAIL_ALIASES = {
    '': {
        'blog_featured': {'size': (1200, 630), 'crop': True, 'quality': 85},
        'blog_preview': {'size': (400, 300), 'crop': True, 'quality': 85},
        'blog_thumb': {'size': (150, 150), 'crop': True, 'quality': 80},
        'admin_thumb': {'size': (100, 75), 'crop': True, 'quality': 75},
    },
}
