from django.urls import path
from . import views

app_name = 'userproperty'

urlpatterns = [
    path('save/<slug:slug>/' , views.UserSaveProperty.as_view() , name = 'save_property'),
    path('unsave/<int:pk>/' , views.UserUnsaveProperty.as_view() , name = 'unsave_property'),
    path('list/' , views.ListSavedPropertiesView.as_view() , name = 'list_saved_properties'),
]