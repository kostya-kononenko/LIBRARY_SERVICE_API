import datetime
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from library.models import Category, Book
from library.serializers import BookListSerializer, BookDetailSerializer
from django.db import models

BOOK_URL = reverse("library:book-list")


def detail_url(book_id: int):
    return reverse("library:book-detail", args=[book_id])


def sample_book(**params):
    category = Category.objects.create(name="Drama")

    defaults = {
        "title": "Test Title",
        "author": "Test Author",
        "description": "Test Description",
        "daily_fee": 0.99,
        "cover": "HARD",
        "created": "2023-09-14T10:07:43.119",
        "updated": "2023-09-14T10:07:43.119",
        "category": category,
    }

    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@user.com", "user12345")
        self.client.force_authenticate(self.user)

    @mock.patch("library.service.get_client_ip")
    def test_list_books(self, mock_get_client_ip):
        mock_get_client_ip.return_value = "127.1.1.1."

        sample_book()
        res = self.client.get(BOOK_URL)
        books = (
            Book.objects.all()
            .annotate(
                rating_user=models.Count(
                    "ratings", filter=models.Q(ratings__ip=mock_get_client_ip)
                )
            )
            .annotate(
                middle_star=models.Sum(models.F("ratings__star"))
                / models.Count(models.F("ratings"))
            )
        )
        serializer = BookListSerializer(books, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()
        url = detail_url(book.id)
        res = self.client.get(url)
        serializer = BookDetailSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        category = Category.objects.create(name="Drama")

        payload = {
            "title": "Test Title",
            "author": "Test Author",
            "description": "Test Description",
            "daily_fee": 0.99,
            "cover": "HARD",
            "created": "2023-09-14T10:07:43.119",
            "updated": "2023-09-14T10:07:43.119",
            "category": category,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_forbidden(self):
        book = sample_book()
        payload = {
            "title": "Test New Title",
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_forbidden(self):
        book = sample_book()
        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "admin12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book_success(self):
        category = Category.objects.create(name="Drama")

        payload = {
            "title": "Test Title",
            "author": "Test Author",
            "description": "Test Description",
            "daily_fee": 12.99,
            "created": datetime.datetime.now(),
            "updated": datetime.datetime.now(),
            "category": category.id,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_book_success(self):
        book = sample_book()
        payload = {
            "title": "New Title",
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_book_success(self):
        book = sample_book()
        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
