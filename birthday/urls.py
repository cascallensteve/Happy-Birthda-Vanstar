from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit-wish/', views.submit_wish, name='submit_wish'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/delete/<int:wish_id>/', views.delete_wish, name='delete_wish'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
]
