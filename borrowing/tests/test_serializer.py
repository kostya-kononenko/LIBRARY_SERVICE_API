import datetime
import json

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.test import APITestCase

from library.models import Book, Category
from borrowing.models import Borrowing
from datetime import timedelta

from borrowing.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingSerializer,
)


BORROWINGS_URL = "/borrowing/"


def create_test_data():
    category = Category.objects.create(name="Fantasy")
    book = Book.objects.create(
        category=category,
        title="Test Book1",
        author="Test Author1",
        description="Test description1",
        daily_fee=1.99,
        created=datetime.datetime.now().strftime("%Y-%m-%d"),
        updated=datetime.datetime.now().strftime("%Y-%m-%d"),
    )
    user = get_user_model().objects.create_user(
        email="user@user.com", password="user12345"
    )
    borrowing = Borrowing.objects.create(
        borrow_date=(datetime.datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        expected_return=(datetime.datetime.now() + timedelta(days=7)).strftime(
            "%Y-%m-%d"
        ),
        book=book,
        user=user,
    )
    return book, borrowing


class BorrowingSerializerTestCase(APITestCase):
    def test_validate(self):
        data = {"expected_return": datetime.datetime.now() - timedelta(days=1)}
        with self.assertRaises(serializers.ValidationError):
            BorrowingSerializer(data=data).is_valid(raise_exception=True)


class BorrowingListSerializerTestCase(APITestCase):
    def test_serialize(self):
        book, borrowing = create_test_data()
        serializer = BorrowingListSerializer(instance=borrowing)
        expected_data = {
            "id": borrowing.id,
            "book": book.title,
            "borrow_date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            "expected_return": (datetime.datetime.now() + timedelta(days=7)).strftime(
                "%Y-%m-%d"
            ),
            "actual_return": None,
            "is_active": True,
        }
        self.assertEqual(serializer.data, expected_data)


class BorrowingDetailSerializerTestCase(APITestCase):
    maxDiff = None

    def test_serialize(self):
        book, borrowing = create_test_data()
        serializer = BorrowingDetailSerializer(instance=borrowing)
        expected_data = {
            "id": borrowing.id,
            "book": {
                "id": book.id,
                "category": book.category.id,
                "title": book.title,
                "author": book.author,
                "image": None,
                "description": book.description,
                "daily_fee": str(book.daily_fee),
                "cover": "hard",
                "created": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                "updated": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                "is_available": False,
            },
            "borrow_date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            "expected_return": (datetime.datetime.now() + timedelta(days=7)).strftime(
                "%Y-%m-%d"
            ),
            "actual_return": None,
            "is_active": True,
        }
        print(json.loads(json.dumps(serializer.data)))
        print(expected_data)
        self.assertEqual(json.loads(json.dumps(serializer.data)), expected_data)
