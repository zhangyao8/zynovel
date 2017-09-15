from django.contrib import admin
from app import models
# Register your models here.
class NovelContentAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

admin.site.register(models.Novel)
admin.site.register(models.NovelContent, NovelContentAdmin)
admin.site.register(models.ReadProgress)