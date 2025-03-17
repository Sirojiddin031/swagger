from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_config'

    def ready(self):
        import app_config.signals  # 🔥 Signalsni avtomatik chaqirish
