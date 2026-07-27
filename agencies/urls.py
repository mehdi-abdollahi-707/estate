from django.urls import path
from . import views

app_name = "agencies"

urlpatterns = [
    path('create/' , views.CreateAgencyView.as_view(), name='create-agency'),
    path('update/' , views.UpdateAgencyView.as_view(), name='update-agency'),
    path('list/' , views.ListAgencyView.as_view(), name='list-of-agencies'),
    path('detail/public/<int:pk>/' , views.DetailPublicAgencyView.as_view(), name='detail-public'),
    path('detail/privet/' , views.DetailPrivetAgencyView.as_view(), name='detail-privet'),
    path('delete/' , views.DeleteAgencyView.as_view(), name='delete-agency'),
]