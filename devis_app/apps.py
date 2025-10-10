from django.apps import AppConfig

class DevisAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'devis_app'

    def ready(self):
        import devis_app.signals
