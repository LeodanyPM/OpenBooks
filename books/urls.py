from django.urls import path
from .views import PublicBookDetailView, PublicBookListView, BookListView, BookDetailView

app_name = "api"

urlpatterns = [
    path("books/", PublicBookListView.as_view(), name="book-list"),
    #path("books/<int:pk>/", PublicBookDetailView.as_view(), name="book-detail"),
    path("book/<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    #path("books/<int:pk>/ratings/", views.RatingListCreateView.as_view(), name="book_ratings"),
    path("explore/", BookListView.as_view(), name="explore"),
    
    ]

