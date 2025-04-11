from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate,get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

UserAccount = get_user_model()
# Serializer for the CustomUser model to expose specific fields in API responses.
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        # Define the model associated with this serializer
        model = UserAccount
        # Specify the fields to be included in the serialized output
        fields = ["id", "name", "email", "role"]
        read_only_fields = ["id", "role"]


# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm Password"
    )
    role = serializers.CharField(read_only=True)

    class Meta:
        model = UserAccount
        fields = ["id", "name", "email", "password", "password2", "role"]
        read_only_fields = ["id", "role"]

    def validate_email(self, value):
        # Check for duplicate email (case-insensitive)
        value = value.lower()
        if UserAccount.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        # Ensure both passwords match and pass validation rules
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        try:
            validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs

    def create(self, validated_data):
        # Remove password2, hash password, and create user
        validated_data.pop("password2")
        password = validated_data.pop("password")
        role = self.context.get("role", "user")
        user = UserAccount(**validated_data, role=role)
        user.set_password(password)
        user.save()
        return user


# Serializer for login (only validates email and password input)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Authenticate the user
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        # Generate JWT token pair (access and refresh tokens)
        refresh = RefreshToken.for_user(user)
        data["access_token"] = str(refresh.access_token)
        data["refresh_token"] = str(refresh)

        return data
