from rest_framework import serializers
from .models import Book, Rating, Report

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Rating
        fields = ["id", "user", "score", "comment", "created_at"]
        read_only_fields = ["user", "created_at"]


class ReportSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Report
        fields = ["id", "user", "reason", "created_at"]
        read_only_fields = ["user", "created_at"]

    def validate_reason(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Reason is required.")
        return value

class ReportedBookSerializer(serializers.ModelSerializer):
    reported_by = serializers.CharField(source="reports.first.user.username")
    reported_at = serializers.DateTimeField(source="reports.first.created_at")
    reason = serializers.CharField(source="reports.first.reason")

    class Meta:
        model = Book
        fields = ["id", "title", "author", "reported_by", "reported_at", "reason"]
