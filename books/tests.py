import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings

from .models import Book, Rating


User = get_user_model()
TEST_MEDIA_ROOT = tempfile.mkdtemp()


def create_user(username):
    return User.objects.create_user(username=username, password="testpass123")


def create_pdf():
    return SimpleUploadedFile(name="test.pdf", content=b"pdf-content", content_type="application/pdf")


def book_data(uploaded_by, **kwargs):
    data = {
        "title": "Libro de prueba",
        "author": "Autor de prueba",
        "description": "Descripción de prueba",
        "file": create_pdf(),
        "license_type": Book.License.PUBLIC_DOMAIN,
        "status": Book.Status.APPROVED,
        "uploaded_by": uploaded_by,
    }

    data.update(kwargs)
    return data


def create_book(uploaded_by, **kwargs):
    return Book.objects.create(**book_data(uploaded_by, **kwargs))


class BookTestMixin:
    def setUp(self):
        super().setUp()

        self.owner = create_user("owner")
        self.reviewer = create_user("reviewer")
        self.other_user = create_user("other")
        self.reader = create_user("reader")
        self.staff_user = User.objects.create_user(username="staff", password="testpass123", is_staff=True)
        
        self.approved_book = create_book(self.owner, status=Book.Status.APPROVED)
        self.pending_book = create_book(self.owner, status=Book.Status.PENDING)
        self.rejected_book = create_book(self.owner, status=Book.Status.REJECTED)

    def build_book(self, **kwargs):
        return Book(**book_data(self.owner, **kwargs))


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class BookModelTests(BookTestMixin, TestCase):
    def test_public_books_returns_only_approved(self):
        public_books = Book.public_books()

        self.assertIn(self.approved_book, public_books)
        self.assertNotIn(self.pending_book, public_books)
        self.assertNotIn(self.rejected_book, public_books)

    def test_is_public(self):
        self.assertTrue(self.approved_book.is_public())
        self.assertFalse(self.pending_book.is_public())
        self.assertFalse(self.rejected_book.is_public())

    def test_approve_book(self):
        self.pending_book.approve(reviewer=self.reviewer, comment="Libro aprobado correctamente.")
        self.pending_book.refresh_from_db()

        self.assertEqual(self.pending_book.status, Book.Status.APPROVED)
        self.assertEqual(self.pending_book.reviewed_by, self.reviewer)
        self.assertIsNotNone(self.pending_book.reviewed_at)
        self.assertEqual(self.pending_book.reviewer_comment, "Libro aprobado correctamente.")

    def test_reject_book(self):
        self.pending_book.reject(reviewer=self.reviewer, comment="El archivo no cumple los requisitos.")
        self.pending_book.refresh_from_db()

        self.assertEqual(self.pending_book.status, Book.Status.REJECTED)
        self.assertEqual(self.pending_book.reviewed_by, self.reviewer)
        self.assertIsNotNone(self.pending_book.reviewed_at)
        self.assertEqual(self.pending_book.reviewer_comment, "El archivo no cumple los requisitos.")

    def test_public_book_can_be_viewed_by_anyone(self):
        self.assertTrue(self.approved_book.can_view(None))
        self.assertTrue(self.approved_book.can_view(self.other_user))

    def test_pending_book_can_be_viewed_by_owner(self):
        self.assertFalse(self.pending_book.can_view(None))
        self.assertFalse(self.pending_book.can_view(self.other_user))
        self.assertTrue(self.pending_book.can_view(self.owner))

    def test_pending_book_can_be_viewed_by_staff(self):
        self.assertTrue(self.pending_book.can_view(self.staff_user))

    def test_clean_original_requires_rights_declaration(self):
        book = self.build_book( license_type=Book.License.ORIGINAL, rights_declaration="")

        with self.assertRaises(ValidationError):
            book.clean()

    def test_clean_original_valid_with_rights_declaration(self):
        book = self.build_book(license_type=Book.License.ORIGINAL, rights_declaration="Declaro que soy el autor de esta obra.")

        book.clean()

    def test_clean_cc_requires_license_detail(self):
        book = self.build_book(license_type=Book.License.CREATIVE_COMMONS, license_detail="")

        with self.assertRaises(ValidationError):
            book.clean()

    def test_file_extension_is_validated(self):
        invalid_file = SimpleUploadedFile(name="malware.exe", content=b"contenido")
        book = self.build_book(file=invalid_file)

        with self.assertRaises(ValidationError):
            book.full_clean()

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class RatingModelTests(BookTestMixin, TestCase):
    def test_can_create_rating_for_approved_book(self):
        rating = Rating.objects.create(book=self.approved_book, user=self.reader, score=5, comment="Muy buen libro.", )

        self.assertEqual(rating.score, 5)
        self.assertEqual(rating.book, self.approved_book)
        self.assertEqual(rating.user, self.reader)

    def test_cannot_rate_own_book(self):
        rating = Rating(book=self.approved_book, user=self.owner, score=5)

        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_cannot_rate_pending_book(self):
        rating = Rating( book=self.pending_book, user=self.reader, score=4)

        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_score_must_be_between_1_and_5(self):
        rating = Rating( book=self.approved_book, user=self.reader, score=6)

        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_unique_rating_per_user_and_book(self):
        Rating.objects.create(book=self.approved_book, user=self.reader, score=4)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Rating.objects.create(book=self.approved_book, user=self.reader, score=5)
                

