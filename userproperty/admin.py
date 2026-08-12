from django.contrib import admin
from .models import SaveProperty


@admin.register(SaveProperty)
class SavePropertyAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "property", "created")
    search_fields = ("user__phone_number", "property__title")
    list_filter = ("created",)
    ordering = ("-created",)
