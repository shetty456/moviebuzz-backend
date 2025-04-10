from rest_framework import serializers
from user.models import CustomUser


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "name", "email", "role"]
        