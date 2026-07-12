from django.urls import path
from .views import *

app_name = 'property'

urlpatterns = [
    path('create/' , CreatePropertyView.as_view() , name='create_property'),
]