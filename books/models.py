import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (FileExtensionValidator, MinValueValidator, MaxValueValidator)
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

# Validators and routes #

MAX_BOOK_FILE_MB = 20

def validate_book_file_size(value):
    max_size = MAX_BOOK_FILE_MB * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(f"The file cannot exceed {MAX_BOOK_FILE_MB} MB.")

def book_file_path(instance, filename):
    """
    Saves files with a unique name. 
    Example: books_file/<uuid>.pdf
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".pdf", ".epub"):
        ext = ".bin"
    unique_name = f"{uuid.uuid4().hex}{ext}"

    return f"books_file/{unique_name}"

# Book #

class Book(models.Model):
    class Status(models.TextChoices):
        PENDING = "P", "Pending"
        APPROVED = "A", "Approved"
        REJECTED = "R", "Rejected"
        REPORTED = "E", "Reported"

    class License(models.TextChoices):
        PUBLIC_DOMAIN = "PD", "Public domain"
        CREATIVE_COMMONS = "CC", "Creative Commons"
        ORIGINAL = "OR", "Original work by the user"

    title = models.CharField("Title", max_length=200)
    author = models.CharField("Author(s)", max_length=200)
    description = models.TextField("Description")

    file = models.FileField("Archive", upload_to=book_file_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "epub"]), validate_book_file_size],
        help_text="Only PDF or ePub.")
    cover = models.ImageField("Cover", upload_to="covers/", null=True, blank=True)
    license_type = models.CharField("License", max_length=2, choices=License.choices)
    license_detail = models.CharField("License details", max_length=200, blank=True, help_text="Example: CC BY-NC 4.0")
    rights_declaration = models.TextField("Statement of Rights", blank=True, help_text="Mandatory for original works.")

    status = models.CharField("State", max_length=1, choices=Status.choices, default=Status.PENDING)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploaded_books", verbose_name="Uploaded by" )
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_books", 
                verbose_name="Reviewed by")
    reviewed_at = models.DateTimeField("Revision date", null=True, blank=True)
    reviewer_comment = models.TextField("Reviewer's comment", blank=True)
    created_at = models.DateTimeField("Created", auto_now_add=True )
    updated_at = models.DateTimeField("Updated", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_absolute_url(self):
        return reverse("books:book-detail", kwargs={"pk": self.pk})

    def is_public(self):
        return self.status == self.Status.APPROVED

    @classmethod
    def public_books(cls):
        return cls.objects.filter(status=cls.Status.APPROVED)
           
    def can_view(self, user):
        """
        Access control. 
        - Approved books are visible to everyone. 
        - Pending or rejected books are visible to their owner. 
        - They are also visible to staff or users  reviewers.
        """
        if self.is_public():
            return True
        if not user or not user.is_authenticated:
            return False
        if self.uploaded_by_id == user.id:
            return True
        return user.is_reviewer()

    def approve(self, reviewer, comment=""):
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.reviewer_comment = comment
        self.save()

    def reject(self, reviewer, comment=""):
        self.status = self.Status.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.reviewer_comment = comment
        self.save()

    def clean(self):
        super().clean()

        if not self.license_type:
            raise ValidationError({"license_type": "Select a license."})
        if self.license_type == self.License.ORIGINAL:
            if not self.rights_declaration:
                raise ValidationError({"rights_declaration": (
                        "The declaration of rights is mandatory "
                        "for original works.")
                                        })

        if self.license_type == self.License.CREATIVE_COMMONS:
            if not self.license_detail:
                raise ValidationError({
                    "license_detail": (
                        "Indicate which Creative Commons license it is. "
                        "Example: CC BY-NC 4.0")
                                        })
    @property
    def file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None

    @property
    def is_pdf(self):
        return self.file_extension == ".pdf"

    @property
    def is_epub(self):
        return self.file_extension == ".epub"

# Rating #

class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="book_ratings")
    score = models.PositiveSmallIntegerField("Score", 
            validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("Comment", blank=True)
    created_at = models.DateTimeField( "Created", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "user"],
                name="unique_rating_per_book_and_user"
            ),
            models.CheckConstraint(
                condition=Q(score__gte=1) & Q(score__lte=5),
                name="rating_score_between_1_and_5"
            ),
        ]

    def clean(self):
        super().clean()
        if self.book_id and self.user_id:
            try:
                book = self.book
            except Book.DoesNotExist:
                return
            if book.uploaded_by_id == self.user_id:
                raise ValidationError("You cannot rate a book that you uploaded.")
            if not book.is_public():
                raise ValidationError("You can only rate approved books.")

    def __str__(self):
        return f"{self.user} → {self.book} ({self.score})"

#Reports"
class Report(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report on {self.book.title} by {self.user.username}"
