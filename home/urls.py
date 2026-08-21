from django.urls import path
from .views import HomeView, ExploreView, BookDetailView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("explore", ExploreView.as_view(), name = "explore"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail") 
]
