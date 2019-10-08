from django.urls import path

from . import views

urlpatterns = [
    path('', views.UploadFile.as_view(), name='index'),
    path('<int:pk>/', views.FileDetails.as_view(), name='detail'),
]