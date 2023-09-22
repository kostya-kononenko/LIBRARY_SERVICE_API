from django_filters import rest_framework as filters

from library.models import Book, Category


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class BookFilter(filters.FilterSet):
    title = CharFilterInFilter(field_name="title", lookup_expr="in")
    author = CharFilterInFilter(field_name="author", lookup_expr="in")

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
        ]


class CategoryFilter(filters.FilterSet):
    name = CharFilterInFilter(field_name="name", lookup_expr="in")

    class Meta:
        model = Category
        fields = [
            "name",
        ]
