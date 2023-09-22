from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.filters import BorrowingFilter
from borrowing.models import Borrowing
from borrowing.permissions import IsAdminOrIfAuthenticatedReadCreateOnly
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 100


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("book")
    permission_classes = (IsAdminOrIfAuthenticatedReadCreateOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BorrowingFilter
    pagination_class = BorrowPagination

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="return",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def return_borrowing(self, request, pk=None):
        """Endpoint for returning a book"""
        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "borrow_date",
                type=OpenApiTypes.DATE,
                description="Filter by borrow_date "
                            "(ex. ?borrow_date=DD-MM-YYYY)",
            ),
            OpenApiParameter(
                "expected_return",
                type=OpenApiTypes.DATE,
                description="Filter by expected_return "
                "(ex. ?expected_return=DD-MM-YYYY)",
            ),
            OpenApiParameter(
                "actual_return",
                type=OpenApiTypes.DATE,
                description="Filter by actual_return "
                "(ex. ?actual_return=DD-MM-YYYY)",
            ),
            OpenApiParameter(
                "book",
                type=OpenApiTypes.STR,
                description="Filter by book (ex. ?book=book)",
            ),
            OpenApiParameter(
                "user",
                type=OpenApiTypes.STR,
                description="Filter by user (ex. ?user=user)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
