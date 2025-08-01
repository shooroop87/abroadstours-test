from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import override as translation_override


class CompleteSitemap(Sitemap):
    """Исправленный sitemap с правильными многоязычными URL"""

    protocol = "https"

    def __init__(self):
        self.languages = [lang[0] for lang in settings.LANGUAGES]

    def items(self):
        """Возвращает кортежи (url_name, language_code)"""
        items = []
        url_names = [
            # Основные страницы
            "index",
            "contact",
            "blog",
            "about",
            "privacy_policy",
            # Туры - категории
            "tours",
            "wine_tours",
            "milano_tours",
            "como_tours",
            # Туры - конкретные
            "alba_barolo_tour",
            "barolo_barbaresco_from_milan",
            "kick_off_walking_tour_in_milano",
            "como_city_walking_tour",
            "lake_como_and_lugano_tour",
            "bellagio_varenna_tour",
            "lake_como_lugano_morcote_tour",
            # Блог
            "lake_como_day_trip",
            "bernina_express_tour",
            "bernina_express_video",
        ]

        for url_name in url_names:
            for lang_code in self.languages:
                items.append((url_name, lang_code))

        return items

    def location(self, item):
        url_name, lang_code = item

        # Используем translation_override для корректной активации языка
        with translation_override(lang_code):
            try:
                url = reverse(url_name)

                # Для языка по умолчанию URL без префикса
                if lang_code == settings.LANGUAGE_CODE:
                    return url
                else:
                    # Для других языков добавляем префикс, если его нет
                    if not url.startswith(f"/{lang_code}/"):
                        url = f"/{lang_code}{url}"
                    return url

            except Exception as e:
                # Если не удалось сгенерировать URL, пропускаем
                error_msg = (
                    f"Ошибка генерации URL для {url_name} " f"на языке {lang_code}: {e}"
                )
                print(error_msg)
                return None

    def lastmod(self, item):
        return timezone.now()

    def priority(self, item):
        url_name, lang_code = item

        if url_name in ["index", "tours", "blog"]:
            return 1.0
        elif url_name in [
            "wine_tours",
            "milano_tours",
            "como_tours",
        ]:
            return 0.9
        elif url_name in [
            "alba_barolo_tour",
            "barolo_barbaresco_from_milan",
            "kick_off_walking_tour_in_milano",
            "como_city_walking_tour",
            "lake_como_and_lugano_tour",
            "bellagio_varenna_tour",
            "lake_como_lugano_morcote_tour",
        ]:
            return 0.8
        elif url_name in [
            "lake_como_day_trip",
            "bernina_express_tour",
            "bernina_express_video",
        ]:
            return 0.7
        else:
            return 0.5

    def changefreq(self, item):
        url_name, lang_code = item

        if url_name in ["index", "blog", "tours"]:
            return "weekly"
        elif url_name in [
            "wine_tours",
            "milano_tours",
            "como_tours",
        ]:
            return "weekly"
        elif "tour" in url_name or "trip" in url_name or url_name == "blog":
            return "monthly"
        else:
            return "monthly"
