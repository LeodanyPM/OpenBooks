from django.urls import path
from .views import SignupPageView, ProfileView


urlpatterns = [
    path("register/", SignupPageView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),    
]


