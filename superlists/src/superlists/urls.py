"""
URL configuration for superlists project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from lists import views as list_views

urlpatterns = [
    path('', list_views.home_page, name='home'),
    #path("lists/the-only-list-in-the-world/", views.home_page, name="view_list"),  # เพิ่มบรรทัดนี้
    #path("lists/the-only-list-in-the-world/", views.view_list, name="view_list"), # เปลี่ยนเป็นเรียก view_list
   # path("lists/<int:list_id>/", views.view_list, name="view_list"),
   # path("lists/new", views.new_list, name="new_list"),  # เพิ่มบรรทัดนี้
    #path("lists/<int:list_id>/add_item", views.add_item, name="add_item"), # เพิ่มบรรทัดนี้
    path("lists/", include("lists.urls")),
    path('about/', list_views.about_page, name='about'),
]
