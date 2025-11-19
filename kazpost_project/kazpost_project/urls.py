# kazpost_project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

# Создаем роутер
router = DefaultRouter()
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'queue', views.QueueTicketViewSet, basename='queue')

urlpatterns = [

    path('', views.terminal_view, name='terminal'), # Главная - будет Терминал
    path('operator/', views.operator_view, name='operator'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('admin/', admin.site.urls),
    # Подключаем URL-адреса нашего API
    path('api/', include(router.urls)),

    # ЭТАП-3
    path('service_desk/', views.service_desk_view, name='service_desk'),
]