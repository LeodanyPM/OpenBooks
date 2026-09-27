from django.views.generic import TemplateView
from django.db.models import Avg
from django.contrib.auth import get_user_model
from books.models import Book, Rating

User = get_user_model()


class HomeView(TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_books"] = (Book.public_books().annotate(rating=Avg("ratings__score")).order_by("-created_at")[:4])
        context["books_count"] = Book.public_books().count()
        context["users_count"] = User.objects.count()
        context["ratings_count"] = Rating.objects.count()
        return context
