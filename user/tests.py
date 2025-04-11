from django.test import TestCase
from user.models import UserAccount
from django.contrib.auth import authenticate


class AccountUserTests(TestCase):
    # Test the creation of a standard user
    def test_create_user(self):
        user = UserAccount.objects.create_user(
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

    def test_create_superuser(self):
        # Test the creation of a superuser (admin)
        admin = UserAccount.objects.create_superuser(
            email="admin@example.com", name="Admin User", password="adminpass"
        )
        self.assertIsNotNone(admin)
        self.assertEqual(admin.email, "admin@example.com")
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        print("✅ test_create_superuser passed")

    def test_create_user_without_email(self):
        # Attempting to create a user without an email should raise a ValueError
        with self.assertRaises(ValueError):
            UserAccount.objects.create_user(
                email="", name="No Email", password="nopassword"
            )
        print("✅ test_create_user_without_email passed")

    def test_default_role_is_user(self):
        # Ensure that users are assigned the default role "user" upon creation
        user = UserAccount.objects.create_user(
            email="rolecheck@example.com", name="Role Check", password="password"
        )
        self.assertEqual(user.role, "user")
        print("✅ test_default_role_is_user passed")

    def test_login_with_correct_credentials(self):
        # Simulate a login using Django's authenticate method with correct credentials
        UserAccount.objects.create_user(
            email="login@example.com", name="Login User", password="correctpassword"
        )

        user = authenticate(email="login@example.com", password="correctpassword")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "login@example.com")
        print("✅ test_login_with_correct_credentials passed")

    def test_login_simulation_by_password_check(self):
        # Directly check password verification using check_password
        user = UserAccount.objects.create_user(
            email="manual@example.com", name="Manual Login", password="mypassword"
        )
        self.assertTrue(user.check_password("mypassword"))
        print("✅ test_login_simulation_by_password_check passed")

    def test_duplicate_email_registration_fails(self):
        # Email field should be unique; creating two users with same email must fail
        UserAccount.objects.create_user(
            email="duplicate@example.com", name="First User", password="password123"
        )
        with self.assertRaises(Exception):
            UserAccount.objects.create_user(
                email="duplicate@example.com",
                name="Second User",
                password="password456",
            )
        print("✅ test_duplicate_email_registration_fails passed")

    def test_user_str_representation(self):
        # Test the __str__ method of the user mode
        user = UserAccount.objects.create_user(
            email="str@example.com", name="Stringy", password="pass"
        )
        self.assertEqual(str(user), "str@example.com")
        print("✅ test_user_str_representation passed")

    def test_login_with_incorrect_password(self):
        UserAccount.objects.create_user(
            email="wrongpass@example.com", name="Wrong Pass", password="correctpass"
        )
        user = authenticate(email="wrongpass@example.com", password="wrongpass")
        self.assertIsNone(user)

    print("✅ test_login_with_incorrect_password passed")

    def test_inactive_user_cannot_authenticate(self):
        user = UserAccount.objects.create_user(
            email="inactive@example.com", name="Inactive", password="password"
        )
        user.is_active = False
        user.save()

        auth_user = authenticate(email="inactive@example.com", password="password")
        self.assertIsNone(auth_user)

    print("✅ test_inactive_user_cannot_authenticate passed")


    def test_create_manager(self):
    # Test the creation of a superuser (admin)
      manager = UserAccount.objects.create_superuser(
        email="manager@example.com", name="manager User", password="managerpass"
     )
      self.assertIsNotNone(manager)
      self.assertEqual(manager.email, "manager@example.com")
      self.assertEqual(manager.role, "manager")
      self.assertTrue(manager.is_staff)
      self.assertTrue(manager.is_superuser)
    print("✅ test_create_manage_user passed")
