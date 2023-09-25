def calculate_total_price_start_borrowing(borrowing):
    days_borrowing = (borrowing.expected_return - borrowing.borrow_date).days
    if days_borrowing == 0:
        price_in_cents = int(borrowing.book.daily_fee * 50)
    else:
        price_in_cents = int(days_borrowing * borrowing.book.daily_fee * 100)
    return price_in_cents


def calculate_total_price_end_borrowing(borrowing):
    days_borrowing = (borrowing.actual_return - borrowing.expected_return).days
    if days_borrowing <= 0:
        price_in_cents = 0
    else:
        price_in_cents = int(days_borrowing * borrowing.book.daily_fee * 200)
    return price_in_cents
