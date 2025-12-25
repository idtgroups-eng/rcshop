
from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        import os
        if os.environ.get("RENDER") == "true":
            from django.contrib.auth.models import User
            if not User.objects.filter(username="rcadmin").exists():
                User.objects.create_superuser(
                    "rcadmin",
                    "idtgroups@gmail.com",
                    "admin123!@#"
                )


