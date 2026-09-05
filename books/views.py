from django.db.models import Avg
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, CreateAPIView
from rest_framework import status as http_status
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from .models import Book, Rating, Report
from .serializers import BookListSerializer, BookDetailSerializer, RatingSerializer, ReportSerializer
from .covers import create_placeholder_cover

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
        
class RatingListCreateView(ListCreateAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.filter(book_id=self.kwargs["pk"])

    def perform_create(self, serializer):
        serializer.save(
            book_id=self.kwargs["pk"],
            user=self.request.user
        )
                
class BookListView(ListView):
    template_name = "explore.html"
    context_object_name = "books"
    paginate_by = 4
    ordering = ["-created_at"]

    def get_queryset(self):
        return Book.public_books().annotate(rating=Avg("ratings__score")).order_by("-created_at")

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

class ReportCreateView(CreateAPIView):
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        book = Book.objects.get(pk=self.kwargs["pk"])
        serializer.save(book=book, user=self.request.user)
        book.status = Book.Status.REPORTED
        book.save()




def read_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if not book.can_view(request.user):
        return HttpResponseForbidden("You are not allowed to read this book.")
    if not book.file:
        return HttpResponseForbidden("This book has no file available.")

    if book.is_public():
        back_url = book.get_absolute_url()
    elif request.user.is_reviewer():
        back_url = reverse("api:moderation-detail", kwargs={"pk": book.pk})
    else:
        back_url = book.get_absolute_url()

    context = {"book": book, "file_url": book.file.url, "back_url": back_url}
    return render(request, "books/read_book.html", context)
    
class BookUploadView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = "books/upload_book.html"
    fields = ["title", "author", "description", "file", "cover",
              "license_type", "license_detail", "rights_declaration"]
    success_url = reverse_lazy("api:explore")

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)

        if not self.object.cover:
            create_placeholder_cover(self.object)
        return response
        
    def get_success_url(self):
        messages.success(self.request, "Your book has been submitted for review. You'll be notified once it's approved.")
        return reverse_lazy("api:explore")
        



class PendingBooksListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "books/moderation/pending_books.html"
    context_object_name = "books"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_reviewer():
            return HttpResponseForbidden("You do not have permission to access the moderation panel.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Book.objects.filter(status=Book.Status.PENDING).select_related("uploaded_by").order_by("-created_at")

def moderation_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # Solo revisores y staff pueden acceder
    if not request.user.is_reviewer():
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Manejar la acción de aprobar/rechazar
    if request.method == "POST":
        action = request.POST.get("action")
        comment = request.POST.get("comment", "").strip()

        if action == "approve":
            book.approve(reviewer=request.user, comment=comment)
            messages.success(request, f"'{book.title}' has been approved.")
            return redirect("api:pending-books")

        elif action == "reject":
            if not comment:
                messages.error(request, "A reason is required to reject a book.")
            else:
                book.reject(reviewer=request.user, comment=comment)
                messages.success(request, f"'{book.title}' has been rejected.")
                return redirect("api:pending-books")

    return render(request, "books/moderation/detail_moderation.html", {"book": book})
