from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .models import Topic


class TopicAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "description", "parent")


admin.site.register(Topic, TopicAdmin)
