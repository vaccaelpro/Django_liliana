from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('Login/', views.login_user, name='login'),
    path('Register/', views.register_user, name='register'),
    path('Logout/', views.logout_user, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('apprentice-dashboard/', views.apprentice_dashboard, name='apprentice_dashboard'),
    path('delete-user/<int:user_id>/', views.user_delete, name='delete_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('cambiar-password/', views.cambiar_password_aprendiz, name='cambiar_password_aprendiz'),
    path('mi-perfil/', views.perfil_aprendiz, name='perfil_aprendiz'),
]