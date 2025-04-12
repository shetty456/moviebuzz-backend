from rest_framework import serializers
from movies.models import Movie,MovieGenre,Language,Genre

# MovieGenre Serializer
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('title','description','language_id','duration','user_id','rate','price') 

# MovieGenre Serializer

class MovieGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieGenre
        fields = ('movie','genre') 

# Language Serializer
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('name',)  

# Genre Serializer
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name')

