from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from user.serializers import RegisterSerializer, LoginSerializer, ProfileSerializer

# Create your views here.
