from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from library.filters import BookFilter, CategoryFilter
from library.models import Book, Category
from library.permissions import IsAdminOrIfAuthenticatedReadOnly
from library.serializers import (
    BookSerializer,
    CategorySerializer,
    BookListSerializer,
    BookDetailSerializer,
)
from library.service import get_client_ip
from django.db import models


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CategoryFilter
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by name (ex. ?name=name)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)