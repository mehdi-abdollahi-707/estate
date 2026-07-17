from django.urls import path
from .views import *

app_name = 'property'

urlpatterns = [
    path('create/' , CreatePropertyView.as_view() , name='create_property'),
    path('list/' , ListPropertyView.as_view() , name='list_property'),
]