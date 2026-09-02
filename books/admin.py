from django.contrib import admin
from .models import Book, Rating, Report


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

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["book", "user", "short_reason", "created_at"]
    list_filter = ["created_at", "book"]
    search_fields = ["book__title", "user__username", "reason"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
    list_per_page = 25

    def short_reason(self, obj):
        if len(obj.reason) > 50:
            return obj.reason[:50] + "..."
        return obj.reason
    short_reason.short_description = "Reason"
