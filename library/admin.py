from django.contrib import admin
from .models import Category, Book, Rating, RatingStarBook


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "daily_fee",
        "created",
        "updated",
    ]
    list_filter = ["created", "updated"]
    list_editable = ["daily_fee"]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "star", "book")


admin.site.register(RatingStarBook)
