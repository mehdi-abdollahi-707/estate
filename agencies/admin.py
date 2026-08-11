from django.contrib import admin
from .models import Agency , Inquiry



@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    """showing fields in main menu"""
    list_display = ("pk" ,'agent' , 'name' , 'license_number' , 'is_verified')

    """filtering items and clicking"""
    search_fields = ('name' , 'license_number' , 'business_phone' , 'agent__phone_number')
    list_filter = ('is_verified' , 'province' , 'city')

    """ordering by """
    ordering = ('-created',)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("pk" , 'property' , 'customer' , 'status' , 'created')
    search_fields = ('property__title' , 'customer__phone_number' , 'message')
    list_filter = ('status',)
    ordering = ('-created',)


