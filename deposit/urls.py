from django.urls import path
from .views import DepositView

urlpatterns=[
    path("",DepositView.as_view(),name="deposit"),
]