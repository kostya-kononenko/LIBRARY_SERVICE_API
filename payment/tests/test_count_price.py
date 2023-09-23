from datetime import timedelta
from unittest.mock import Mock

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from library.models import Book, Category
from borrowing.models import Borrowing
from borrowing.count_borrowing import (
    count_total_price_start_borrowing,
    count_total_price_end_borrowing,
)
from payment.stripe import create_payment
from payment.tests.test_model import CURRENT_DAY, BORROWING_DAYS


class StripeTest(TestCase):
    def setUp(self):
        self.email = "user@user.com"
        self.password = "user12345"

        self.user = get_user_model().objects.create_user(
            email=self.email, password=self.password
        )

        self.category = Category.objects.create(name="Drama")

        self.book = Book.objects.create(
            category=self.category,
            title="Test Book",
            author="Test Author",
            description="Test description",
            daily_fee=Decimal(0.99),
            cover="hard",
            created="2023-09-14T10:07:43.119",
            updated="2023-09-14T10:07:43.119",
        )

        self.borrowing = Borrowing.objects.create(
            expected_return=CURRENT_DAY + timedelta(days=BORROWING_DAYS),
            book=self.book,
            user=self.user,
        )

    def test_count_total_start_borrowing(self):
        self.borrowing.borrow_date = CURRENT_DAY
        self.borrowing.expected_return = CURRENT_DAY + timedelta(days=BORROWING_DAYS)

        self.borrowing.save()

        price_in_cents = count_total_price_start_borrowing(self.borrowing)
        expected_price_in_cents = 296

        self.assertEqual(price_in_cents, expected_price_in_cents)

    def test_count_total_end_borrowing(self):
        borrowing_days_delay = 6

        self.borrowing.expected_return = CURRENT_DAY + timedelta(days=BORROWING_DAYS)
        self.borrowing.actual_return = self.borrowing.expected_return + timedelta(
            days=borrowing_days_delay
        )

        self.borrowing.save()

        expected_price_in_cents = count_total_price_end_borrowing(self.borrowing)
        total_price_in_cents = 1187

        self.assertEqual(expected_price_in_cents, total_price_in_cents)
