import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from books.models import Book, Report

User = get_user_model()
TEST_MEDIA_ROOT = tempfile.mkdtemp()

def create_user(username, **kwargs):
    return User.objects.create_user(username=username, password="testpass123", **kwargs)

def create_pdf():
    return SimpleUploadedFile(
        name="test.pdf", content=b"%PDF-1.4 test", content_type="application/pdf"
    )

def create_book(uploaded_by, **kwargs):
    defaults = {"title": "Test Book",
        "author": "Test Author",
        "description": "Test description",
        "file": create_pdf(),
        "license_type": Book.License.PUBLIC_DOMAIN,
        "status": Book.Status.APPROVED,
        "uploaded_by": uploaded_by}
    defaults.update(kwargs)
    return Book.objects.create(**defaults)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class BookAccessProtectionTests(TestCase):
    def setUp(self):
        self.owner = create_user("owner")
        self.reader = create_user("reader")
        self.pending_book = create_book(self.owner, status=Book.Status.PENDING)

    def _detail_url(self, book):
        return reverse("api:book-detail", kwargs={"pk": book.pk})

    def test_anonymous_cannot_view_pending_book(self):
        response = self.client.get(self._detail_url(self.pending_book))
        self.assertIn(response.status_code, [302, 403, 404])

    def test_other_user_cannot_view_pending_book(self):
        self.client.login(username="reader", password="testpass123")
        response = self.client.get(self._detail_url(self.pending_book))
        self.assertIn(response.status_code, [403, 404])

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class RatingProtectionTests(TestCase):

    def setUp(self):
        self.owner = create_user("owner")
        self.reviewer = create_user("reviewer", role="reviewer")
        self.public_book = create_book(self.owner, status=Book.Status.APPROVED)
        self.pending_book = create_book(self.owner, status=Book.Status.PENDING)

    def _rating_url(self, book):
        return reverse("api:book-ratings", kwargs={"pk": book.pk})

    def test_anonymous_cannot_rate(self):
        response = self.client.post(self._rating_url(self.public_book), {"score": 5, "comment": "Great"})
        self.assertIn(response.status_code, [401, 403])

    def test_owner_cannot_rate_own_book(self):
        self.client.login(username="owner", password="testpass123")
        response = self.client.post(self._rating_url(self.public_book), {"score": 5, "comment": "My book is great"})
        self.assertIn(response.status_code, [400, 403])

    def test_reviewer_cannot_rate_pending_book(self):
        self.client.login(username="reviewer", password="testpass123")
        response = self.client.post(self._rating_url(self.pending_book), {"score": 5, "comment": "Good"})
        self.assertIn(response.status_code, [400, 403, 404])

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ReportProtectionTests(TestCase):
    
    def setUp(self):
        self.owner = create_user("owner")
        self.public_book = create_book(self.owner, status=Book.Status.APPROVED)

    def _report_url(self, book):
        return reverse("api:book-report", kwargs={"pk": book.pk})

    def test_anonymous_cannot_report(self):
        response = self.client.post(self._report_url(self.public_book), {"reason": "Spam"})
        self.assertIn(response.status_code, [401, 403])


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ModerationProtectionTests(TestCase):
    def setUp(self):
        self.owner = create_user("owner")
        self.reader = create_user("reader")
        self.pending_book = create_book(self.owner, status=Book.Status.PENDING)

    def test_anonymous_cannot_access_moderation(self):
        url = reverse("api:moderation-detail", kwargs={"pk": self.pending_book.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])

    def test_normal_user_cannot_approve_book(self):
        self.client.login(username="reader", password="testpass123")
        url = reverse("api:moderation-detail", kwargs={"pk": self.pending_book.pk})
        response = self.client.post(url, {"action": "approve", "comment": "OK"})
        self.assertIn(response.status_code, [403, 302])
        
        self.pending_book.refresh_from_db()
        self.assertEqual(self.pending_book.status, Book.Status.PENDING)
