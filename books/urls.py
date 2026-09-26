from django.urls import path
from . import views
app_name = "books"

urlpatterns = [
    path("<int:pk>/ratings/", views.RatingListCreateView.as_view(), name="book-ratings"),
    path("", views.PublicBookListView.as_view(), name="book-list"),
    #path("books/<int:pk>/", PublicBookDetailView.as_view(), name="book-detail"),
    path("<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
    path("<int:pk>/report/", views.ReportCreateView.as_view(), name="book-report"),
    path("<int:pk>/read/", views.read_book, name="read"),
    path("upload/", views.BookUploadView.as_view(), name="upload"),
    path("moderation/", views.PendingBooksListView.as_view(), name="pending-books"),
    path("moderation/detail/<int:pk>/", views.moderation_detail, name="moderation-detail"),
    path("moderation/reported-books/", views.ReportedBooksListView.as_view(), name="reported-books"),
    path("moderation/reported/<int:pk>/", views.review_report, name="reported-detail"),
    #path("books/<int:pk>/ratings/", views.RatingListCreateView.as_view(), name="book_ratings"),
    path("explore/", views.BookListView.as_view(), name="explore"),
    path("search/", views.SearchResultsListView.as_view(), name="search-results"),
]
    

