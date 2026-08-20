from django.urls import path
from .views import HomeView, ExploreView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("explore", ExploreView.as_view(), name = "explore") 
]
