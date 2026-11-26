from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('acceso/', views.LoginSIGCE.as_view(), name='login'),
    path('salir/', views.logout_user, name='logout'),
    path('panel/', views.dashboard, name='dashboard'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('solicitudes/nueva/', views.solicitud_nueva, name='solicitud_nueva'),
    path('solicitudes/<int:pk>/', views.solicitud_detalle, name='solicitud_detalle'),
    path('solicitudes/<int:pk>/editar/', views.solicitud_editar, name='solicitud_editar'),
    path('solicitudes/<int:pk>/participantes/nuevo/', views.participante_nuevo, name='participante_nuevo'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/nuevo/', views.usuario_nuevo, name='usuario_nuevo'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/clave/', views.usuario_clave, name='usuario_clave'),
]