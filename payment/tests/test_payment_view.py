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
from payment.serializers import PaymentListSerializer, PaymentDetailSerializer
from payment.tests.test_model import CURRENT_DAY, BORROWING_DAYS

PAYMENT_URL = reverse("payment:payment-list")


def detail_url(payment_id):
    return reverse("payment:payment-detail", args=[payment_id])


class UnauthenticatedPaymentApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        request = self.client.get(PAYMENT_URL)

        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@user.com",
            "user12345",
        )

        self.another_user = get_user_model().objects.create_user(
            "user1@user.com",
            "user12345",
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

        self.borrowing_user = Borrowing.objects.create(
            expected_return=CURRENT_DAY + timedelta(days=BORROWING_DAYS),
            book=self.book,
            user=self.user,
        )

        self.borrowing_another_user = Borrowing.objects.create(
            expected_return=CURRENT_DAY + timedelta(days=BORROWING_DAYS),
            book=self.book,
            user=self.another_user,
        )

        self.money_to_pay = round(self.book.daily_fee * BORROWING_DAYS, 2)

        self.payment_user = Payment.objects.create(
            status="PENDING",
            payment_type="PAYMENT",
            borrowing=self.borrowing_user,
            session_url="https://checkout.stripe.com/c/pay/cs_test",
            session_id="cs_test",
            money_to_pay=self.money_to_pay,
            user=self.user,
        )

        self.payment_another_user = Payment.objects.create(
            status="PENDING",
            payment_type="PAYMENT",
            borrowing=self.borrowing_user,
            session_url="https://checkout.stripe.com/c/pay/cs_test1",
            session_id="cs_test1",
            money_to_pay=self.money_to_pay,
            user=self.another_user,
        )

    def test_retrieve_payment_detail(self):
        payments = Payment.objects.all()

        url = detail_url(payments[0].id)

        request = self.client.get(url)

        serializer = PaymentDetailSerializer(payments[0])

        self.assertEqual(request.status_code, status.HTTP_200_OK)

        self.assertEqual(serializer.data["id"], request.data["id"]),
        self.assertEqual(serializer.data["user"], request.data["user"]),
        self.assertEqual(serializer.data["status"], request.data["status"]),
        self.assertEqual(serializer.data["payment_type"], request.data["payment_type"]),
        self.assertEqual(
            serializer.data["borrowing_book"], request.data["borrowing_book"]
        ),
        self.assertEqual(
            serializer.data["expected_return"], request.data["expected_return"]
        ),
        self.assertEqual(serializer.data["session_url"], request.data["session_url"]),
        self.assertEqual(serializer.data["session_id"], request.data["session_id"]),
        self.assertEqual(serializer.data["money_to_pay"], request.data["money_to_pay"])

    def test_create_payment_forbidden(self):
        payload = {
            "status": "PENDING",
            "payment_type": "PAYMENT",
            "borrowing": self.borrowing_user,
            "session_url": "https://checkout.stripe.com/c/pay/cs_test1",
            "session_id": "cs_test1",
            "money_to_pay": self.money_to_pay,
            "user": self.user,
        }

        request = self.client.post(PAYMENT_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)


class AdminPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="admin12345",
            is_staff=True,
        )
        self.user = get_user_model().objects.create_user(
            "user@user.com",
            "user12345",
        )

        self.client.force_authenticate(self.admin)

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

        self.borrowing_admin = Borrowing.objects.create(
            expected_return=CURRENT_DAY + timedelta(days=BORROWING_DAYS),
            book=self.book,
            user=self.admin,
        )

        self.borrowing_user = Borrowing.objects.create(
            expected_return=CURRENT_DAY + timedelta(days=BORROWING_DAYS),
            book=self.book,
            user=self.user,
        )

        self.money_to_pay = round(self.book.daily_fee * BORROWING_DAYS, 2)

        self.payment_admin = Payment.objects.create(
            status="PENDING",
            payment_type="PAYMENT",
            borrowing=self.borrowing_admin,
            session_url="https://checkout.stripe.com/c/pay/cs_test",
            session_id="cs_test",
            money_to_pay=self.money_to_pay,
            user=self.admin,
        )

        self.payment_user = Payment.objects.create(
            status="PENDING",
            payment_type="PAYMENT",
            borrowing=self.borrowing_admin,
            session_url="https://checkout.stripe.com/c/pay/cs_test1",
            session_id="cs_test1",
            money_to_pay=self.money_to_pay,
            user=self.user,
        )

    def test_create_payment_not_allowed(self):
        payload = {
            "status": "PENDING",
            "payment_type": "PAYMENT",
            "borrowing": self.borrowing_admin,
            "session_url": "https://checkout.stripe.com/c/pay/cs_test1",
            "session_id": "cs_test1",
            "money_to_pay": self.money_to_pay,
            "user": self.admin,
        }

        request = self.client.post(PAYMENT_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_payment_not_allowed(self):
        url = detail_url(self.payment_admin.id)

        request = self.client.delete(url)

        self.assertEqual(request.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
