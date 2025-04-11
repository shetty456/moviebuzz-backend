from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from user.serializers import RegisterSerializer
from drf_spectacular.utils import extend_schema
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@extend_schema(request=RegisterSerializer, responses={201: RegisterSerializer})
@api_view(["POST"])
def register_user(request):
    """
    Register a new user.
    """

    data = request.data.copy()
    data["role"] = "user"
    serializer = RegisterSerializer(data=data, context={"role": "user"})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    return Response(
        {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema(request=RegisterSerializer, responses={201: RegisterSerializer})
@api_view(["POST"])
def register_manager(request):
    data = request.data.copy()
    data["role"] = "manager"
    serializer = RegisterSerializer(data=data, context={"role": "manager"})
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "message": "Manager registered",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            },
            status=201,
        )
    return Response(serializer.errors, status=400)


@extend_schema(request=RegisterSerializer, responses={201: RegisterSerializer})
@api_view(["POST"])
def register_admin(request):
    data = request.data.copy()
    data["role"] = "admin"
    serializer = RegisterSerializer(data=data, context={"role": "admin"})
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "message": "Admin registered",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            },
            status=201,
        )

    return Response(serializer.errors, status=400)
