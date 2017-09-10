from django.contrib import admin
from app import models
# Register your models here.
admin.site.register(models.Novel)
admin.site.register(models.NovelContent)
admin.site.register(models.ReadProgress)