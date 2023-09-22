import datetime

from rest_framework import serializers

import borrowing
from borrowing.models import Borrowing
from borrowing.tasks import (
    send_message_of_borrowing_return_email,
    send_message_of_borrowing_creation_email,
    send_message_of_borrowing_creation_telegram,
    send_message_of_borrowing_return_telegram,
)
from library.serializers import BookSerializer
from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.stripe import create_stripe_session
from user.models import User


class BorrowingSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    expected_return = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    actual_return = serializers.DateTimeField(format="%d-%m-%Y %H:%M")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return",
            "actual_return",
            "is_active",
        )
        read_only_fields = ("id", "is_active", "borrow_date")


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(many=False,
                                        read_only=True,
                                        slug_field="title")
    borrow_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    expected_return = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    actual_return = serializers.DateTimeField(format="%d-%m-%Y %H:%M")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return",
            "actual_return",
            "is_active",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    borrow_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    expected_return = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    actual_return = serializers.DateTimeField(format="%d-%m-%Y %H:%M")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return",
            "actual_return",
            "is_active",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    message = serializers.CharField(
        max_length=63,
        default="Make a payment first for a successful "
                "borrowing book by link below",
        read_only=True,
    )
    payments = PaymentSerializer(many=True,
                                 read_only=True)
    book_title = serializers.CharField(source="book.title",
                                       read_only=True)
    book_author = serializers.CharField(source="book.author",
                                        read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "message",
            "payments",
            "book",
            "book_title",
            "book_author",
            "borrow_date",
            "expected_return",
        )

    def validate(self, attrs):
        book = attrs.get("book")
        expected_return = attrs.get("expected_return")

        if expected_return <= datetime.datetime.today():
            raise serializers.ValidationError(
                "Expected return date must " "be later than borrow date."
            )

        if book.is_available is False:
            raise serializers.ValidationError(
                f"This book is for rent, please "
                f"choose another one. End date of "
                f"borrowing for this book "
                f"{expected_return}"
            )
        return attrs

    def create(self, validated_data):
        book = validated_data["book"]
        user = self.context["request"].user
        borrowing = Borrowing.objects.create(
            book=book,
            expected_return=validated_data["expected_return"],
            user=user,
        )
        book.save()
        create_stripe_session(borrowing, request=self.context["request"])
        if user.user_notification == "email":
            send_message_of_borrowing_creation_email(borrowing, user)
        else:
            send_message_of_borrowing_creation_telegram(borrowing)
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    message = serializers.CharField(
        max_length=63,
        default="Make a payment first for a "
                "successful borrowing return book "
                "by link below",
        read_only=True,
    )
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "message",
            "payments",
        )
        read_only_fields = (
            "message",
            "payments",
        )

    def validate(self, attrs):
        borrowing = self.instance
        if borrowing.actual_return:
            raise serializers.ValidationError(
                "This borrowing has already been returned."
            )
        return attrs

    def update(self, instance, validated_data):
        user = self.context["request"].user
        instance.actual_return = datetime.datetime.today()
        instance.save()
        create_stripe_session(instance, self.context.get("request"))
        if user.user_notification == "email":
            send_message_of_borrowing_return_email(instance, user)
        else:
            send_message_of_borrowing_return_telegram(instance)
        return instance
