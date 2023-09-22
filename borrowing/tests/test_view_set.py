import datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from library.models import Book, Category
from borrowing.models import Borrowing
from datetime import date, timedelta

BORROWINGS_URL = "/borrowing/"


class BorrowingViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="user12345",
        )
        self.admin_user = get_user_model().objects.create_user(
            email="admin@admin.com", password="admin12345", is_staff=True
        )

        self.category = Category.objects.create(name="Fantasy")

        self.book = Book.objects.create(
            category=self.category,
            title="Test Book1",
            author="Test Author1",
            description="Test description1",
            cover="SOFT",
            daily_fee=1.99,
            created="2023-09-14T10:07:43.119",
            updated="2023-09-14T10:07:43.119",
        )
        self.borrowing_data = {
            "borrow_date": date.today(),
            "expected_return": date.today() + timedelta(days=7),
            "book": self.book,
            "user": self.user,
        }


class AuthenticatedUserBorrowingViewSetTestCase(BorrowingViewSetTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        Borrowing.objects.create(
            expected_return=date.today() + timedelta(days=3),
            book=self.book,
            user=self.user,
        )

    def test_list_borrowings_authenticated(self):
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_borrowing_authenticated(self):
        data = {
            "expected_return": (datetime.datetime.now() + timedelta(days=14)).strftime(
                "%Y-%m-%d"
            ),
            "book": self.book,
        }
        response = self.client.post(BORROWINGS_URL, data)
        print(data)
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_return_borrowing_authenticated(self):
        borrowing = Borrowing.objects.create(
            expected_return=date.today() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        self.assertIsNone(borrowing.actual_return)
        self.assertTrue(borrowing.is_active)

        url_return = BORROWINGS_URL + str(borrowing.id) + "/return/"
        response = self.client.patch(url_return)
        borrowing.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(borrowing.actual_return)
        self.assertFalse(borrowing.is_active)
        borrowing.refresh_from_db()


class NotAuthenticatedUserBorrowingViewSetTestCase(BorrowingViewSetTestCase):
    def test_list_borrowings_unauthenticated(self):
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_unauthenticated(self):
        data = {
            "expected_return": date.today() + timedelta(days=14),
            "book": self.book.id,
        }
        response = self.client.post(BORROWINGS_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_return_borrowing_unauthenticated(self):
        borrowing = Borrowing.objects.create(
            expected_return=date.today() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )

        url_return = BORROWINGS_URL + str(borrowing.id) + "/return/"
        response = self.client.patch(url_return)
        borrowing.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(borrowing.actual_return)
        self.assertTrue(borrowing.is_active)
