from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),
    path('monthly/', views.monthly_report, name='monthly_report'),
    path('category/', views.category_report, name='category_report'),
    path('export/', views.export_data, name='export_data'),
]