from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_scores, name='employee_scores'),
    path('upload/', views.upload_file, name='upload_file'),
]
