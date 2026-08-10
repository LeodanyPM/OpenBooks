from django.urls import path
from .views import SignupPageView

urlpatterns = [
    path("register/", SignupPageView.as_view(), name="register"),
]
