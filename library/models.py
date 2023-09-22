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
