from .views import AnalyticsDashboardView
from django.urls import path

urlpatterns = [
    path("analytics/dashboard/", AnalyticsDashboardView.as_view()),
]