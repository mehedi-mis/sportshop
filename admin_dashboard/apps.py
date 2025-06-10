from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AdminDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_dashboard'
    
    def ready(self):
        from django.contrib.sites.models import Site
        from django.conf import settings

        def create_default_site(sender, **kwargs):
            Site.objects.update_or_create(
                id=settings.SITE_ID,
                defaults={
                    'domain': '127.0.0.1:8000',  # Or your real domain
                    'name': 'Sports Shop',
                }
            )

        post_migrate.connect(create_default_site, sender=self)
