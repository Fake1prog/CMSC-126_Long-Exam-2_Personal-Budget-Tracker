from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('add/', views.category_add, name='category_add'),
    path('edit/<int:category_id>/', views.category_edit, name='category_edit'),
    path('delete/<int:category_id>/', views.category_delete, name='category_delete'),
]