from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.serializers import RegisterSerializer
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from user.models import UserAccount, Profile
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from user.permissions import IsAdminorReadonly,IsUser


@method_decorator(csrf_exempt, name="dispatch")
class RegisterUserView(APIView):
    """
    Register a new user with default role 'user'.
    """

    role = "user"

    @extend_schema(request=RegisterSerializer, responses={201: RegisterSerializer})
    def post(self, request):
        data = request.data.copy()
        data["role"] = self.role
        serializer = RegisterSerializer(data=data, context={"role": self.role})

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": f"{self.role.capitalize()} registered successfully",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "role": user.role,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterManagerView(RegisterUserView):
    """
    Register a new manager.
    """

    role = "manager"


class RegisterAdminView(RegisterUserView):
    """
    Register a new admin.
    """

    role = "admin"


class LoginView(APIView):
    """
    Authenticate user and return access and refresh tokens.
    Shows response based on user role (user/admin/manager).
    """

    @extend_schema(request=LoginSerializer, responses={200: LoginSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = UserAccount.objects.get(email=request.data["email"])
            role = user.role

            return Response(
                {
                    "message": "Login successfulas {role}",
                    "role": role,
                    "access_token": serializer.validated_data["access_token"],
                    "refresh_token": serializer.validated_data["refresh_token"],
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Blacklist the refresh token to log the user out securely.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None,
        responses={204: None},
        description="Logout user by blacklisting the refresh token.",
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT
            )
        except KeyError:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TokenError:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: ProfileSerializer},
        request=ProfileSerializer,
        description="Get or update your profile information.",
    )
    def get_object(self):
        return Profile.objects.get(user=self.request.user)
class Updateview(APIView):
    permission_classes = [IsAdminorReadonly]

    def get(request):
        return {"msg:u are admin"}
    
class GetUserview(APIView):
    permission_classes = [IsUser]

    def get(request):
        return {"msg:u are User"}    

        

