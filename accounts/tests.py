from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="l",
            email="l@email.com",
            password="testpass123"
        )
        self.assertEqual(user.username, "l")
        self.assertEqual(user.email, "l@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.role, "reader") 

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@email.com",
            password="testpass123"
        )
        self.assertEqual(admin_user.username, "superadmin")
        self.assertEqual(admin_user.email, "superadmin@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        
class RegisterViewTests(TestCase):
    def test_register_view_get(self):
        """GET a /accounts/register/ debe devolver código 200 y usar la plantilla correcta."""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_register_view_post_success(self):
        """POST con datos válidos crea un usuario y redirige al login."""
        response = self.client.post(reverse("register"), {
            "username": "testuser",
            "email": "test@email.com",
            "password1": "testpass123",
            "password2": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        
        # Verificar que el usuario fue creado
        user = get_user_model().objects.get(username="testuser")
        self.assertEqual(user.email, "test@email.com")
        self.assertEqual(user.role, "reader")  

    def test_register_view_post_invalid(self):
        """POST con contraseñas no coincidentes no crea usuario y muestra errores."""
        initial_count = get_user_model().objects.count()
        response = self.client.post(reverse("register"), {
            "username": "testuser2",
            "email": "test2@email.com",
            "password1": "testpass123",
            "password2": "differentpass",
        })
        self.assertEqual(response.status_code, 200)
        # ✅ Verifica que el mensaje de error esté en el HTML
        self.assertContains(response, "The two password fields didn’t match.")
        self.assertEqual(get_user_model().objects.count(), initial_count)

class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="testpass123"
        )
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.home_url = reverse("home")

    def test_login_view_get(self):
        """GET a /accounts/login/ debe devolver 200 y usar la plantilla correcta."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_success(self):
        """POST con credenciales correctas redirige a home (LOGIN_REDIRECT_URL)."""
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "testpass123"
        })
        self.assertRedirects(response, self.home_url)
        # Verificar que el usuario está autenticado
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_login_fail(self):
        """POST con credenciales incorrectas no autentica y muestra error."""
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_logout_view(self):
        """POST a /accounts/logout/ redirige a home y cierra la sesión."""
        self.client.login(username="testuser", password="testpass123")
        self.assertTrue(self.client.session.get('_auth_user_id'))
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.home_url)
        self.assertFalse(self.client.session.get('_auth_user_id'))
