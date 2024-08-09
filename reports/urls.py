from django.urls import path
from . import views

urlpatterns = [
  path('/', views.home, name='home'),
  path('/upload/', views.upload_files, name='upload_files'),
  path('/scores/', views.employee_scores, name='employee_scores'),
]
