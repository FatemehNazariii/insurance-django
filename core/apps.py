
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.contrib import admin
        admin.site.site_header = "پنل مدیریت بیمه ایمنو"
        admin.site.site_title = "ایمنو"
        admin.site.index_title = "خوش آمدید"
