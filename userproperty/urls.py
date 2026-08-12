from django.urls import path
from . import views

app_name = 'userproperty'

urlpatterns = [
    path('add/<slug:slug>/' , views.UserSaveProperty.as_view() , name = 'add_property'),
]