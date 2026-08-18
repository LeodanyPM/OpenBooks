from django.db.models import Avg
from rest_framework.generics import ListAPIView, RetrieveAPIView

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
        return (Book.public_books()
                .annotate(rating_avg=Avg("ratings__score"))
                )
