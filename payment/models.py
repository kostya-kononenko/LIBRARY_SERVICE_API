from django.db import models

from borrowing.models import Borrowing
from user.models import User


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        PAID = "Paid", "Paid"

    class Types(models.TextChoices):
        PAYMENT = "Payment", "Payment"
        FINE = "Fine", "Fine"

    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING
    )
    payment_type = models.CharField(
        max_length=63,
        choices=Types.choices,
        default=Types.PAYMENT
    )
    session_url = models.URLField()
    session_id = models.CharField(
        max_length=63,
        unique=True)
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0)
    user = models.ForeignKey(
        User,
        related_name="payments",
        on_delete=models.CASCADE)
    borrowing = models.ForeignKey(
        Borrowing,
        related_name="payments",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return (f"Payment {self.id} "
                f"({self.payment_type}) "
                f"{self.user.email}")
from django.db import models

# Create your models here.
