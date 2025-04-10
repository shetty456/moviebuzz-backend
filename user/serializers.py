from rest_framework import serializers
from user.models import CustomUser


# Serializer for the CustomUser model to expose specific fields in API responses.
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        # Define the model associated with this serializer
        model = CustomUser
        # Specify the fields to be included in the serialized output
        fields = ["id", "name", "email", "role"]
        