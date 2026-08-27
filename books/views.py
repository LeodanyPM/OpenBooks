from django.db.models import Avg
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.views.generic import ListView, DetailView

from .models import Book
from .serializers import BookListSerializer, BookDetailSerializer


class PublicBookListView(ListAPIView):
    serializer_class = BookListSerializer

    def get_queryset(self):
        return (Book.public_books()
                .annotate(rating_avg=Avg("ratings__score"))
                .order_by("-created_at")
                )


class PublicBookDetailView(RetrieveAPIView):
    serializer_class = BookDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Book.public_books().annotate(rating_avg=Avg("ratings__score"))
                
class BookListView(ListView):
    template_name = "explore.html"
    context_object_name = "books"
    paginate_by = 1
    ordering = ["-created_at"]

    def get_queryset(self):
        return Book.public_books().annotate(rating=Avg("ratings__score"))

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ["books/list_books.html"]
        return [self.template_name]
        
class BookDetailView(DetailView):
    model = Book
    template_name = "books/detail_book.html"
    context_object_name = "book"

    def get_queryset(self):
        return Book.objects.annotate(rating=Avg("ratings__score")).prefetch_related("ratings__user")
