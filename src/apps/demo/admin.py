from django.contrib import admin

from apps.demo.models import Data


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    pass
