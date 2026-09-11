from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import SignupPageView, ProfileView


urlpatterns = [
    path("register/", SignupPageView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),    
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
