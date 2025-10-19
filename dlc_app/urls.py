from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework import routers

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'losses', views.LossViewSet)
router.register(r'categories', views.CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('losses-by-product/', views.losses_by_product, name='losses_by_product'),
    path('losses-by-month/', views.losses_by_month, name='losses_by_month'),
    path('api/losses/download-losses-pdf/', views.download_losses_pdf, name='download-losses-pdf'),
    path('reminders/', views.reminders, name='reminders'),
]