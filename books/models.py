import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (FileExtensionValidator, MinValueValidator, MaxValueValidator)
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

# Validadores y rutas #

MAX_BOOK_FILE_MB = 20


def validate_book_file_size(value):
    max_size = MAX_BOOK_FILE_MB * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(f"El archivo no puede superar {MAX_BOOK_FILE_MB} MB.")

def book_file_path(instance, filename):
    """
    Guarda archivos con nombre único.
    Ejemplo: media/books/3/a1b2c3d4.pdf
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".pdf", ".epub"):
        ext = ".bin"

    user_id = instance.uploaded_by_id or "unassigned"
    unique_name = f"{uuid.uuid4().hex}{ext}"

    return f"books/{user_id}/{unique_name}"

# Book #

class Book(models.Model):
    class Status(models.TextChoices):
        PENDING = "P", "Pendiente"
        APPROVED = "A", "Aprobado"
        REJECTED = "R", "Rechazado"

    class License(models.TextChoices):
        PUBLIC_DOMAIN = "PD", "Dominio público"
        CREATIVE_COMMONS = "CC", "Creative Commons"
        ORIGINAL = "OR", "Obra original del usuario"

    title = models.CharField("Título", max_length=200)
    author = models.CharField("Autor(es)", max_length=200)
    description = models.TextField("Descripción")

    file = models.FileField("Archivo", upload_to=book_file_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "epub"]), validate_book_file_size],
        help_text="Solo PDF o ePub.")

    license_type = models.CharField("Licencia", max_length=2, choices=License.choices)
    license_detail = models.CharField("Detalle de licencia", max_length=200, blank=True, help_text="Ejemplo: CC BY-NC 4.0")
    rights_declaration = models.TextField("Declaración de derechos", blank=True, help_text="Obligatoria para obras originales.")

    status = models.CharField("Estado", max_length=1, choices=Status.choices, default=Status.PENDING)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploaded_books", verbose_name="Subido por" )
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_books", 
                verbose_name="Revisado por")
    reviewed_at = models.DateTimeField("Fecha de revisión", null=True, blank=True)
    reviewer_comment = models.TextField("Comentario del revisor", blank=True)
    created_at = models.DateTimeField("Creado", auto_now_add=True )
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_absolute_url(self):
        return reverse("books:detail", kwargs={"pk": self.pk})

    def is_public(self):
        return self.status == self.Status.APPROVED

    @classmethod
    def public_books(cls):
        return cls.objects.filter(status=cls.Status.APPROVED)

    def can_view(self, user):
        """
        Control de acceso.
        - Los libros aprobados los ve todo el mundo.
        - Los pendientes/rechazados los ve su dueño.
        - También los ve staff o usuarios del grupo Reviewers.
        """
        if self.is_public():
            return True
        if not user or not user.is_authenticated:
            return False
        if self.uploaded_by_id == user.id:
            return True
        return user.is_staff or user.groups.filter(name="Reviewers").exists()

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
            raise ValidationError({"license_type": "Selecciona una licencia."})
        if self.license_type == self.License.ORIGINAL:
            if not self.rights_declaration:
                raise ValidationError({"rights_declaration": (
                        "La declaración de derechos es obligatoria "
                        "para obras originales.")
                                        })

        if self.license_type == self.License.CREATIVE_COMMONS:
            if not self.license_detail:
                raise ValidationError({
                    "license_detail": (
                        "Indica qué licencia Creative Commons es. "
                        "Ejemplo: CC BY-NC 4.0")
                                        })

# Rating #

class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="book_ratings")
    score = models.PositiveSmallIntegerField("Puntuación", 
            validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("Comentario", blank=True)
    created_at = models.DateTimeField( "Creado", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"
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
                raise ValidationError("No puedes valorar un libro que tú subiste.")
            if not book.is_public():
                raise ValidationError("Solo puedes valorar libros aprobados.")

    def __str__(self):
        return f"{self.user} → {self.book} ({self.score})"
