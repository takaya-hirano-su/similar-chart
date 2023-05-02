from django.urls import path
from .views import get  

urlpatterns=[
    path("",view=get,name="portfolio"),
]