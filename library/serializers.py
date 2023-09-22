from rest_framework import serializers

from library.models import Book, Category, Rating


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
        )

