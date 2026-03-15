from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class RegisterViewTests(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        })

        self.assertRedirects(response, reverse("blog:post_list"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

        # check logged in
        response = self.client.get(reverse("accounts:settings"))
        self.assertEqual(response.status_code, 200)

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user(
            username="existinguser",
            email="old@example.com",
            password="pass12345"
        )

        response = self.client.post(reverse("accounts:register"), {
            "username": "existinguser",
            "email": "new@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="existinguser").count(), 1)


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass12345"
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "pass12345",
        })

        self.assertRedirects(response, reverse("blog:post_list"))

    def test_login_with_invalid_credentials_shows_error(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "wrongpassword",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")


class SettingsAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="settingsuser",
            email="settings@example.com",
            password="pass12345"
        )

    def test_settings_requires_login(self):
        response = self.client.get(reverse("accounts:settings"))
        login_url = reverse("accounts:login")
        settings_url = reverse("accounts:settings")
        self.assertRedirects(response, f"{login_url}?next={settings_url}")

    def test_logged_in_user_can_access_settings(self):
        self.client.login(username="settingsuser", password="pass12345")
        response = self.client.get(reverse("accounts:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/settings.html")