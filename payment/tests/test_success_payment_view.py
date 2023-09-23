import datetime
from datetime import timedelta

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from library.models import Book, Category
from borrowing.models import Borrowing

from payment.models import Payment

from payment.tests.test_model import CURRENT_DAY, BORROWING_DAYS


def success_url(borrowing_id):
    return reverse("payment:payment-success", args=[borrowing_id])


class SuccessPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@user.com",
            "user123456",
        )

        self.client.force_authenticate(self.user)

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

        self.money_to_pay = round(self.book.daily_fee * BORROWING_DAYS, 2)

        self.payment = Payment.objects.create(
            status="PAID",
            payment_type="PAYMENT",
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/c/pay/cs_test",
            session_id="cs_test",
            money_to_pay=self.money_to_pay,
            user=self.user,
        )

    def test_get_success_payment(self):
        url = success_url(self.borrowing.id)

        expected_status = "PAID"

        self.borrowing.refresh_from_db()
        self.payment.refresh_from_db()

        self.assertEqual(self.payment.status, expected_status)
