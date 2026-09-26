import tempfile
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from books.models import Book

User = get_user_model()
TEST_MEDIA_ROOT = tempfile.mkdtemp()

def create_test_file():
    return SimpleUploadedFile("test.pdf", b"pdf_content", content_type="application/pdf")


class CustomUserTests(TestCase):
    def test_create_user_defaults(self):
        user = User.objects.create_user(username="l", email="l@email.com", password="testpass123")
        self.assertEqual(user.username, "l")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.role, "reader")

    def test_is_reviewer_logic(self):
        reader = User.objects.create_user(username="reader", password="pass", role="reader")
        reviewer = User.objects.create_user(username="reviewer", password="pass", role="reviewer")
        staff = User.objects.create_user(username="staff", password="pass", is_staff=True)

        self.assertFalse(reader.is_reviewer())
        self.assertTrue(reviewer.is_reviewer())
        self.assertTrue(staff.is_reviewer()) 


class RegisterViewTests(TestCase):
    def test_register_view_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_register_view_post_success(self):
        response = self.client.post(reverse("register"), {
            "username": "testuser", "email": "test@email.com",
            "password1": "testpass123", "password2": "testpass123"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@email.com")
        self.assertEqual(user.role, "reader")  

    def test_register_view_post_invalid(self):
        initial_count = User.objects.count()
        response = self.client.post(reverse("register"), {
            "username": "testuser2", "email": "test2@email.com",
            "password1": "testpass123", "password2": "differentpass"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "password fields didn") 
        self.assertEqual(User.objects.count(), initial_count)


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@email.com", password="testpass123")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.home_url = reverse("home")

    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_success(self):
        response = self.client.post(self.login_url, {"username": "testuser", "password": "testpass123"})
        self.assertRedirects(response, self.home_url)
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_login_fail(self):
        response = self.client.post(self.login_url, {"username": "testuser", "password": "wrongpassword"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_logout_view(self):
        self.client.login(username="testuser", password="testpass123")
        self.assertTrue(self.client.session.get('_auth_user_id'))
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.home_url)
        self.assertFalse(self.client.session.get('_auth_user_id'))

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProfileViewTests(TestCase):    
    def setUp(self):
        self.user = User.objects.create_user(username="profileuser", password="testpass123")
        self.profile_url = reverse("profile")

    def test_profile_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_profile_context_data_separation(self):
        self.client.login(username="profileuser", password="testpass123")
        Book.objects.create(title="Public Book", author="Author A", description="Desc",
            file=create_test_file(), license_type=Book.License.PUBLIC_DOMAIN,
            status=Book.Status.APPROVED, uploaded_by=self.user)
        Book.objects.create(title="Pending Book", author="Author B", description="Desc",
            file=create_test_file(), license_type=Book.License.PUBLIC_DOMAIN,
            status=Book.Status.PENDING, uploaded_by=self.user)
        
        other_user = User.objects.create_user(username="other", password="pass")
        Book.objects.create(title="Other Public Book", author="Author C", description="Desc",
            file=create_test_file(), license_type=Book.License.PUBLIC_DOMAIN,
            status=Book.Status.APPROVED, uploaded_by=other_user)

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["public_count"], 1)
        self.assertEqual(response.context["non_public_count"], 1)

        public_titles = [b.title for b in response.context["public_books"]]
        non_public_titles = [b.title for b in response.context["non_public_books"]]

        self.assertIn("Public Book", public_titles)
        self.assertNotIn("Other Public Book", public_titles)
        self.assertIn("Pending Book", non_public_titles)
