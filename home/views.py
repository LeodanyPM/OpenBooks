from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"
    
class ExploreView(TemplateView):
    template_name = "books/list_books.html"
