from django.contrib import admin
from .models import Property , PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    can_delete = True
    fields = ('image',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = (PropertyImageInline,)
    list_display = ("pk" ,'agency' , 'title' , 'created')