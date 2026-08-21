from django.urls import path
from .views import PublicBookDetailView, PublicBookListView, RatingListCreateView

app_name = "api"

urlpatterns = [
    path("books/", PublicBookListView.as_view(), name="book-list"),
    path("books/<int:pk>/", PublicBookDetailView.as_view(), name="book-detail"),
    path("books/<int:pk>/ratings/", views.RatingListCreateView.as_view(), name="book_ratings"),
    ]
path("books/<int:pk>/", views.BookDetailView.as_view(), name="book_detail")
