from django.test import TestCase
from django.contrib.auth import get_user_model

from library.models import Book, Category
from borrowing.models import Borrowing
from datetime import date, timedelta


BORROWINGS_URL = "/borrowing/"


class BorrowingModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com", password="admin12345"
        )

        self.category = Category.objects.create(name="Drama")

        self.book = Book.objects.create(
            category=self.category,
            title="Test Book",
            author="Test Author",
            description="Test description",
            daily_fee=0.99,
            created="2023-09-14T10:07:43.119",
            updated="2023-09-14T10:07:43.119",
        )
        self.borrowing_data = {
            "expected_return": date.today() + timedelta(days=7),
            "book": self.book,
            "user": self.user,
        }

    def test_borrowing_creation(self):
        borrowing = Borrowing.objects.create(**self.borrowing_data)
        self.assertEqual(Borrowing.objects.count(), 1)
        self.assertEqual(
            borrowing.expected_return, self.borrowing_data["expected_return"]
        )
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)
        self.assertIsNone(borrowing.actual_return)
        self.assertTrue(borrowing.is_active)

    def test_borrowing_return(self):
        borrowing = Borrowing.objects.create(**self.borrowing_data)
        borrowing.actual_return = date.today()
        borrowing.save()
        self.assertFalse(borrowing.is_active)

    def test_borrowing_str_representation(self):
        borrowing = Borrowing(**self.borrowing_data)
        self.assertEqual(str(borrowing), str(borrowing.borrow_date))
