from django.urls import path
from .views import TradeTrainingView

urlpatterns=[
    path("",TradeTrainingView.as_view(),name="trade"),
]