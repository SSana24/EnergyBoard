from django.urls import path
from .views import upload_csv,data_list

urlpatterns = [
    path('upload/', upload_csv, name='upload_csv'),
    path('data/', data_list, name='data_list'),  
]