# LIBRARY SERVICE API

The RESTful API for a library service platform. 


## User Registration and Authentication:

- Users can register with their email and password to create an account.
- Users can login with their credentials and receive a JWT token for authentication.
- Users can logout and invalidate their JWT token.

## User Profile:
- Users can create and update their profile, including profile picture and other details.
- Users can retrieve their own profile.

## Library
- User with admin permission can create/update/retrieve/delete books and category.
- User who is authenticated can retrieve books and category.

## Borrowing
- User with admin permission can create/update/retrieve/delete borrowing.
- User who is authenticated can create/retrieve/return borrowing.

## Rating system
- User with admin permission can create/update/retrieve/delete rating.
- User who is authenticated can create/retrieve rating for all books (only one time).

## Payment system (using Stripe)
- User who is authenticated can create payments and pay for a start 
  rent the book and can pay for end rent the book.

## User notifications (using Celery and Redis / Email or Telegram):
- When a user rents/returns a book, a message about this is sent to 
  the user by mail or in a telegram channel
- When the user does not return the book within the specified period, 
- he is sent a daily message about the debt by mail or in a telegram channel

## Filtering system
- User who is authenticated can filtering next endpoint: 
    - Borrowing (by borrow_date, expected_return, actual_return, book, user);
    - Book (by title, author);
    - Category (by name);

## API Permissions:
- Only authenticated users can perform actions such as creating borrowing/payment and add stars to the book.
- User with admin permission can create/update/retrieve/delete user profile, book, category, borrowing, payment, 
- Users can update their own profile.
- User can use token authentication (JWT)

## API Documentation:
- The API well-documented with clear instructions on how to use each endpoint.
- The documentation include sample API requests and responses for different endpoints.

## Tests
- You can tests next endpoint:
  - borrowing;
  - book;
  - category;
  - payment;

## Database
- Using Postgres database

## How to installing using GitHub

- Clone this repository
- Create venv: python -m venv venv
- Activate venv: source venv/bin/activate
- Install requirements: pip install -r requirements.txt
- Run: python manage.py runserver
- Create user via: user/register
- Get access token via: user/token


## Diagram of all models:

![library_book](https://github.com/kostya-kononenko/LIBRARY_SERVICE_API/assets/107486491/0a0ef652-3ae4-4f99-9d42-fc52b19f23df)
