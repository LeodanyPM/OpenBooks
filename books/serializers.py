from django.urls import reverse
from rest_framework import serializers

from .models import Book


class BookListSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ["id", "title", "author", "rating", "detail_url"]

    def get_rating(self, obj):
        rating_avg = getattr(obj, "rating_avg", None)

        if rating_avg is None:
            return 0

        return float(round(rating_avg, 2))

    def get_detail_url(self, obj):
        url = reverse("api:book-detail", kwargs={"pk": obj.pk})
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(url)

        return url


class BookDetailSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    license = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    read_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ["id", "title", "author", "description", "rating", "license", "ratings", "read_url"]

    def get_rating(self, obj):
        rating_avg = getattr(obj, "rating_avg", None)

        if rating_avg is None:
            return 0

        return float(round(rating_avg, 2))

    def get_license(self, obj):
        license_info = {
            "type": obj.license_type,
            "name": obj.get_license_type_display(),
            "detail": obj.license_detail or None,
        }

        if obj.license_type == Book.License.ORIGINAL:
            license_info["rights_declaration"] = obj.rights_declaration or None

        return license_info

    def get_ratings(self, obj):
        ratings = (
            obj.ratings
            .select_related("user")
            .order_by("-created_at")[:3]
        )

        return [
            {
                "user": rating.user.username,
                "score": rating.score,
                "comment": rating.comment,
            }
            for rating in ratings
        ]

    def get_read_url(self, obj):
        return None
