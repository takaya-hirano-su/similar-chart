from django.contrib import admin
from django.urls import path,include
from .views import index,IndexView

urlpatterns=[
    path("",IndexView.as_view(),name="index"),
]