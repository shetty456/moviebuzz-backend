from django.test import TestCase
from django.contrib.auth import authenticate, get_user_model
from django.test import Client
from user.models import Profile

User = get_user_model()


class AccountUserTests(TestCase):

    # Test the creation of a standard user
    def test_create_user(self):

        user = User.objects.create_user(
            email="testuser@example.com", name="Test User", password="securepassword123"
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.name, "Test User")
        self.assertTrue(user.check_password("securepassword123"))
        self.assertEqual(user.role, "user")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        print("✅ test_create_user passed")

    # Test the creation of a superuser (admin)
    def test_create_superuser(self):

        admin = User.objects.create_superuser(
            email="admin@example.com", name="Admin User", password="adminpass"
        )
        self.assertIsNotNone(admin)
        self.assertEqual(admin.email, "admin@example.com")
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        print("✅ test_create_superuser passed")

    # Test creating a user without an email should raise an error
    def test_create_user_without_email(self):

        with self.assertRaises(ValueError):
            User.objects.create_user(email="", name="No Email", password="nopassword")
        print("✅ test_create_user_without_email passed")

    # Test that the default role for a user is "user"
    def test_default_role_is_user(self):

        user = User.objects.create_user(
            email="rolecheck@example.com", name="Role Check", password="password"
        )
        self.assertEqual(user.role, "user")
        print("✅ test_default_role_is_user passed")

    # Test login with correct credentials
    def test_login_with_correct_credentials(self):

        User.objects.create_user(
            email="login@example.com", name="Login User", password="correctpassword"
        )

        user = authenticate(email="login@example.com", password="correctpassword")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "login@example.com")
        print("✅ test_login_with_correct_credentials passed")

    # Test login by manually checking password
    def test_login_simulation_by_password_check(self):

        user = User.objects.create_user(
            email="manual@example.com", name="Manual Login", password="mypassword"
        )
        self.assertTrue(user.check_password("mypassword"))
        print("✅ test_login_simulation_by_password_check passed")

    # Test that creating two users with the same email will raise an error
    def test_duplicate_email_registration_fails(self):

        User.objects.create_user(
            email="duplicate@example.com", name="First User", password="password123"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="duplicate@example.com",
                name="Second User",
                password="password456",
            )
        print("✅ test_duplicate_email_registration_fails passed")

    # Test the __str__ method of the user model
    def test_user_str_representation(self):

        user = User.objects.create_user(
            email="str@example.com", name="Stringy", password="pass"
        )
        self.assertEqual(str(user), "str@example.com")
        print("✅ test_user_str_representation passed")

    # Test login with incorrect password should fail
    def test_login_with_incorrect_password(self):

        User.objects.create_user(
            email="wrongpass@example.com", name="Wrong Pass", password="correctpass"
        )
        user = authenticate(email="wrongpass@example.com", password="wrongpass")
        self.assertIsNone(user)
        print("✅ test_login_with_incorrect_password passed")

    # Test that inactive users cannot authenticate
    def test_inactive_user_cannot_authenticate(self):

        user = User.objects.create_user(
            email="inactive@example.com", name="Inactive", password="password"
        )
        user.is_active = False
        user.save()

        auth_user = authenticate(email="inactive@example.com", password="password")
        self.assertIsNone(auth_user)
        print("✅ test_inactive_user_cannot_authenticate passed")

    # Test the creation of a manager user
    def test_create_manager(self):

        # Create a manager user
        manager = User.objects.create_user(
            email="manager@example.com", name="Manager User", password="managerpass"
        )
        # Set the role and permissions
        manager.role = "manager"
        manager.is_staff = True
        manager.is_superuser = True
        manager.save()

        self.assertIsNotNone(manager)
        self.assertEqual(manager.email, "manager@example.com")
        self.assertEqual(manager.role, "manager")
        self.assertTrue(manager.is_staff)
        self.assertTrue(manager.is_superuser)
        print("✅ test_create_manager passed")


class LogoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email="logoutuser@example.com", name="Logout User", password="logoutpass"
        )

    def test_logout(self):

        login = self.client.login(email="logoutuser@example.com", password="logoutpass")
        self.assertTrue(login)

        response = self.client.logout()

        self.assertNotIn("_auth_user_id", self.client.session)
        print("✅ test_logout passed")


class ProfileTests(TestCase):
    # Test the creation and access of a user profile
    def test_user_profile_creation(self):

        user = User.objects.create_user(
            email="profileuser@example.com", name="Profile User", password="profilepass"
        )

        profile = Profile.objects.create(
            user=user, bio="Hello world!", location="Earth"
        )

        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.bio, "Hello world!")
        self.assertEqual(profile.location, "Earth")
        self.assertEqual(str(profile), "Profile of profileuser@example.com")
        print("✅ test_user_profile_creation passed")
