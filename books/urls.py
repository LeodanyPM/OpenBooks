from django.urls import path
from .views import PublicBookDetailView, PublicBookListView

app_name = "api"

urlpatterns = [
    path("books/", PublicBookListView.as_view(), name="book-list"),
    path("books/<int:pk>/", PublicBookDetailView.as_view(), name="book-detail"),
    ]
