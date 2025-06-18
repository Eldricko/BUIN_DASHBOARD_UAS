from django.urls import path
from . import views

urlpatterns = [
    path('charts/', views.chart_view, name='chart_view'),
]
