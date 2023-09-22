from django_filters import rest_framework as filters

from borrowing.models import Borrowing


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class BorrowingFilter(filters.FilterSet):
    borrow_date = filters.DateTimeFromToRangeFilter()
    expected_return = filters.DateTimeFromToRangeFilter()
    actual_return = filters.DateTimeFromToRangeFilter()
    book = CharFilterInFilter(field_name="book", lookup_expr="in")
    user = CharFilterInFilter(field_name="user", lookup_expr="in")

    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return",
            "actual_return",
            "book",
            "user",
        ]
