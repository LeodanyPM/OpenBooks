from django.urls import path
from .views import PublicBookDetailView, PublicBookListView, BookListView, BookDetailView, RatingListCreateView, ReportCreateView, read_book, BookUploadView, PendingBooksListView, moderation_detail, ReportedBooksListView

app_name = "api"

urlpatterns = [
    path("books/<int:pk>/ratings/", RatingListCreateView.as_view(), name="book-ratings"),
    path("books/", PublicBookListView.as_view(), name="book-list"),
    #path("books/<int:pk>/", PublicBookDetailView.as_view(), name="book-detail"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("books/<int:pk>/report/", ReportCreateView.as_view(), name="book-report"),
    path("books/<int:pk>/read/", read_book, name="read"),
    path("upload/", BookUploadView.as_view(), name="upload"),
    path("moderation/", PendingBooksListView.as_view(), name="pending-books"),
    path("moderation/detail/<int:pk>/", moderation_detail, name="moderation-detail"),
    path("moderation/reported-books/", ReportedBooksListView.as_view(), name="reported-books"),
    #path("books/<int:pk>/ratings/", views.RatingListCreateView.as_view(), name="book_ratings"),
    path("explore/", BookListView.as_view(), name="explore"),
    ]

