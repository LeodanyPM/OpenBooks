from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, IntegerField
from books.models import Book
from .forms import CustomUserCreationForm


class SignupPageView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "registration/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        public_books = Book.objects.filter(uploaded_by=self.request.user, status=Book.Status.APPROVED).order_by("-created_at")
        non_public_books = self.get_non_public_books()
        context.update({ "public_books": public_books, "non_public_books": non_public_books,
            "public_count": public_books.count(), "non_public_count": non_public_books.count()})
        return context

    def get_non_public_books(self):
        status_order = Case(
            When(status=Book.Status.PENDING, then=0),
            When(status=Book.Status.REPORTED, then=1),
            When(status=Book.Status.REJECTED, then=2),
            output_field=IntegerField())
        return (Book.objects.filter(uploaded_by=self.request.user).exclude(status=Book.Status.APPROVED).annotate(status_order=status_order)
            .order_by("status_order", "-created_at"))
