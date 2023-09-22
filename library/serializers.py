from rest_framework import serializers

from library.models import Book, Category, Rating


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
        )


class BookSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    updated = serializers.DateTimeField(format="%d-%m-%Y %H:%M")

    class Meta:
        model = Book
        fields = (
            "id",
            "category",
            "title",
            "author",
            "image",
            "description",
            "daily_fee",
            "cover",
            "created",
            "updated",
            "is_available",
        )


class BookListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    middle_star = serializers.IntegerField()
    rating_user = serializers.BooleanField()

    class Meta:
        model = Book
        fields = (
            "id",
            "category",
            "title",
            "author",
            "image",
            "description",
            "daily_fee",
            "cover",
            "created",
            "updated",
            "category",
            "middle_star",
            "rating_user",
            "is_available",
        )


class BookDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "category",
            "title",
            "author",
            "image",
            "description",
            "daily_fee",
            "cover",
            "created",
            "updated",
            "category",
            "is_available",
        )


class CreateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("star", "book", "ip")

        def create(self, validate_data):
            rating = Rating.objects.update_or_create(
                ip=validate_data.get("ip", None),
                airplane=validate_data.get("airplane", None),
                defaults={"star": validate_data.get("star")},
            )
            return rating
