from django.apps import AppConfig

class ToursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tours'
    verbose_name = 'Tours Management'
    
    def ready(self):
        # Импортируем сигналы если будут нужны
        try:
            import tours.signals
        except ImportError:
            pass
