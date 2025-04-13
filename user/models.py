from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils import timezone
from django.conf import settings

# Custom manager to handle user creation logic
class CustomUserManager(BaseUserManager):
    
     def create_user(self, email, name, password=None, role="user"):
            """
            Creates and returns a user with the given email, name, password, and role.
            """
            if not email:
                raise ValueError("The email field is required")
            email = self.normalize_email(email)
            user = self.model(email=email, name=name, role=role)
            user.set_password(password)
            user.save()
            return user

     def create_superuser(self, email, name, password):
        """
        Creates and returns a superuser with admin privileges.
        """
        user = self.create_user(email, name, password, role="admin")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Custom user model extending AbstractBaseUser and PermissionsMixin
class UserAccount (AbstractBaseUser, PermissionsMixin):
    # Define user roles
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
        ("manager", "Manager"),
    )
    # Model fields
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="user")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    # Link to the custom manager
    objects = CustomUserManager()
    # Configuration for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        """String representation of the user object."""
        return self.email
    
    @property
    def Is_Admin_role(self):
         return self.role == 'admin'
    
    @property
    def Is_User_role(self):
         return self.role == 'user'
    
    @property
    def Is_Manager_role(self):
         return self.role == 'manager'
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
    
    @property
    def Is_Admin_role(self):
         return self.role == 'Admin'
    
    @property
    def Is_User_role(self):
         return self.role == 'User'
    
    @property
    def Is_Manager_role(self):
         return self.role == 'Manager'
    
