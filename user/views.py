from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from user.serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


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
