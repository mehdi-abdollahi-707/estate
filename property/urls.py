from django.urls import path
from .views import *

app_name = 'property'

urlpatterns = [
    path('create/' , CreatePropertyView.as_view() , name='create_property'),
    path('list/' , ListPropertyView.as_view() , name='list_property'),
    path('detail/<slug:slug>/' , PropertyDetailView.as_view() , name='detail_property'),
    path('update/<slug:slug>/' , UpdatePropertyView.as_view() , name='update_property'),
    path('delete/<slug:slug>/' , DeletePropertyView.as_view() , name='delete_property'),
]