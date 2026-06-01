from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
     path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
]
