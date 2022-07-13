from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    # signals has to be "started" manually by importing the module
    def ready(self):
        """
        Executes signals at start
        """
        import api.signals
