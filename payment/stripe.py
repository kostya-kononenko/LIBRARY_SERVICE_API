import stripe

from django.urls import reverse

from borrowing.count_borrowing import (
    count_total_price_start_borrowing,
    count_total_price_end_borrowing,
)
from main import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment(borrowing, session):
    payment = Payment.objects.create(
        status="PENDING",
        payment_type="PAYMENT",
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        user=borrowing.user,
    )
    if borrowing.actual_return is None:
        payment.money_to_pay = round(
            count_total_price_start_borrowing(borrowing) / 100, 2
        )
        payment.save()
    else:
        payment.money_to_pay = round(
            count_total_price_end_borrowing(borrowing) / 100, 2
        )
        payment.save()
    return payment


def create_stripe_session(borrowing, request):
    success_url = (
        request.build_absolute_uri(
            reverse("payment:payment-success", args=[borrowing.id])
        )
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = (
        request.build_absolute_uri(
            reverse("payment:payment-cancel", args=[borrowing.id])
        )
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    if borrowing.actual_return is None:
        total_price_in_cents = count_total_price_start_borrowing(borrowing)
    else:
        total_price_in_cents = count_total_price_end_borrowing(borrowing)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": total_price_in_cents,
                    "product_data": {
                        "name": borrowing.book.title,
                        "description": f"User: {borrowing.user.email}",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    payment = create_payment(borrowing, session)
    borrowing.payments.add(payment)
    borrowing.save()
    return session.url
