import datetime

from celery import shared_task
from django.core.mail import send_mail

from main import settings
from telebot import TeleBot
from borrowing.models import Borrowing

bot = TeleBot(token=settings.TELEGRAM_TOKEN)


@shared_task(name="send_message_of_borrowing_creation_email")
def send_message_of_borrowing_creation_email(borrow, user):
    subject = f"You have borrowed {borrow.id} "
    message = (
        f"Dear {user.first_name} {user.last_name},\n\n"
        f"You have successfully borrowed the book: "
        f"{borrow.book.title} | {borrow.book.author},\n\n"
        f"Borrow date: {borrow.borrow_date},\n\n"
        f"Expected return date: {borrow.expected_return},\n\n"
    )
    mail_sent = send_mail(
        subject,
        message,
        "kkononenko3@gmail.com",
        [user.email]
    )
    return mail_sent


@shared_task(name="send_overdue_debt_email")
def send_overdue_debt_email():
    for detail in Borrowing.objects.all().filter(
        expected_return__lt=datetime.datetime.now()
    ):
        subject = f"You have overdue debt {detail.id} "
        message = (
            f"Dear {detail.user.first_name} {detail.user.last_name},\n\n"
            f"You have overdue debt by borrowed the book: "
            f"{detail.book.title} | {detail.book.author},\n\n"
            f"Borrow date: {detail.borrow_date},\n\n"
            f"Expected return date: {detail.expected_return},\n\n"
        )
        mail_sent = send_mail(
            subject,
            message,
            "kkononenko3@gmail.com",
            [detail.user.email]
        )
        return mail_sent


@shared_task(name="send_message_of_borrowing_return_email")
def send_message_of_borrowing_return_email(borrow, user):
    subject = f"You have return borrowed {borrow.id} "
    message = (
        f"Dear {user.first_name} {user.last_name},\n\n"
        f"You have successfully return borrowed book: "
        f"{borrow.book.title} | {borrow.book.author},\n\n"
        f"Borrow date: {borrow.borrow_date},\n\n"
        f"Expected return date: {borrow.expected_return},\n\n"
        f"Actual return date: {borrow.actual_return},\n\n"
    )
    mail_sent = send_mail(
        subject,
        message,
        "kkononenko3@gmail.com",
        [user.email]
    )
    return mail_sent


@shared_task(name="send_message_of_borrowing_creation_telegram")
def send_message_of_borrowing_creation_telegram(borrowing: Borrowing) -> None:
    message = (
        f"📒CREATE NEW BORROWING:📒\n\n"
        f"ID: {borrowing.id}\n"
        f"User: {borrowing.user.email}\n"
        f"Book title: {borrowing.book.title}\n"
        f"Book author: {borrowing.book.author}\n"
        f"Borrow date: {borrowing.borrow_date}\n"
        f"Expected return date: {borrowing.expected_return}\n"
        f"Payment status: ✅\n"
    )
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


@shared_task(name="send_overdue_debt_telegram")
def send_overdue_debt_telegram():
    for detail in Borrowing.objects.all().filter(
        expected_return__lt=datetime.datetime.now()
    ):
        message = (
            f"📒YOU HAVE OVERDUE DEBT:📒\n\n"
            f"ID: {detail.id}\n"
            f"User: {detail.user.email}\n"
            f"Book title: {detail.book.title}\n"
            f"Book author: {detail.book.author}\n"
            f"Borrow date: {detail.borrow_date}\n"
            f"Expected return date: {detail.expected_return}\n"
        )
        bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


@shared_task(name="send_message_of_borrowing_return_telegram")
def send_message_of_borrowing_return_telegram(borrowing: Borrowing) -> None:
    message = (
        f"📗RETURNED THE BORROWING:📗\n\n"
        f"ID: {borrowing.id}\n"
        f"User: {borrowing.user.email}\n"
        f"Book title: {borrowing.book.title}\n"
        f"Book author: {borrowing.book.author}\n"
        f"Borrow date: {borrowing.borrow_date}\n"
        f"Actual return date: {borrowing.actual_return}\n"
        f"Expected return date: {borrowing.expected_return}\n"
        f"Payment status: ✅\n"
    )
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
