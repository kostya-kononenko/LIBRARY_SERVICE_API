from django.db import models

from borrowing.models import Borrowing


class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "hard", "hard"
        SOFT = "soft", "soft"

    category = models.ForeignKey(
        Category,
        related_name="books",
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    image = models.ImageField(upload_to="books/%Y/%m/%d",
                              blank=True)
    description = models.TextField(blank=True)
    daily_fee = models.DecimalField(max_digits=10,
                                    decimal_places=2)
    cover = models.CharField(max_length=25,
                             choices=Cover.choices,
                             default=Cover.HARD)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def is_available(self):
        return not self.borrowings.filter(
            actual_return__isnull=True).exists()

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(
                fields=[
                    "id",
                ]
            ),
            models.Index(fields=["title"]),
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return self.title


class RatingStarBook(models.Model):
    value = models.PositiveSmallIntegerField("Meaning", default=0)

    def __str__(self):
        return f"{self.value}"

    class Meta:
        verbose_name = "Star rating"
        verbose_name_plural = "Rating Stars"
        ordering = ["-value"]


class Rating(models.Model):
    ip = models.CharField("IP address",
                          max_length=15)
    star = models.ForeignKey(
        RatingStarBook,
        on_delete=models.CASCADE,
        verbose_name="star"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="ratings")

    def __str__(self):
        return f"{self.star} - {self.book}"

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
