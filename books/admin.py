from django.contrib import admin
from .models import Book, Rating


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "license_type", "uploaded_by", "created_at",)

    list_filter = ("status", "license_type",)

    search_fields = ("title", "author", "uploaded_by__username",)

    ordering = ("-created_at",)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "score", "created_at")

    list_filter = ("score",)

    search_fields = ("book__title", "user__username")

    ordering = ("-created_at",)
