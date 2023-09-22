from django.db import models


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return = models.DateTimeField()
    actual_return = models.DateTimeField(blank=True, null=True)
    book = models.ForeignKey(
        "library.Book",
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="borrowings"
    )

    @property
    def is_active(self):
        return self.actual_return is None

    class Meta:
        ordering = ["expected_return"]
        verbose_name = "borrowing"
        verbose_name_plural = "borrowings"

    def __str__(self) -> str:
        return str(self.borrow_date)
