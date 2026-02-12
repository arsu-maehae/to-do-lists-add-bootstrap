# src/calculator/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ตรง views.calculator_page ต้องตรงกับชื่อฟังก์ชันใน views.py ของคุณ
    path('', views.calculator_page, name='calculator'),
    path('js/', views.js_cal, name='js_cal'),
    path('django/', views.django_cal, name='calc_django'),
]