Project Overview

The Library Management System is a backend API built using Django and Django REST Framework (DRF).
It helps manage library operations like adding books, registering users, and tracking borrow/return transactions.

The project simulates a real-world backend workflow — focusing on API design, authentication, database management, and deployment.

 Features
 Books Management

Create, Read, Update, and Delete (CRUD) operations for books.

Each book includes: title, author, ISBN, published date, and number of copies available.

ISBNs are unique per book.

 User Management

Manage users with CRUD operations.

Each user includes: username, email, membership date, and active status.

 Borrowing and Returning Books

Users can borrow available books.

When a book is checked out, available copies decrease.

Returning a book increases the available copies.

Tracks checkout and return dates per user.

 Authentication

Built-in Django authentication system for secure login and session management.

Optionally supports token or JWT-based authentication (can be added later).

 Tech Stack

Python 3.x

Django 5.x

Django REST Framework

SQLite3 (default)

Optional: Deployable on Heroku or PythonAnywhere

 Installation & Setup
1 Clone the repository
git clone https://github.com/your-username/library-management-system.git
cd library-management-system

2 Create a virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate   # On Mac/Linux

3 Install dependencies
pip install -r requirements.txt

4 Run migrations
python manage.py migrate

 Create a superuser
python manage.py createsuperuser

Start the server
python manage.py runserver


Your app will be live at  http://127.0.0.1:8000/

 Quick Access Links
Description	URL
Admin Panel	http://127.0.0.1:8000/admin/

Admin Login	http://127.0.0.1:8000/admin/login/

Admin Logout	http://127.0.0.1:8000/admin/logout/

API Login (DRF)	http://127.0.0.1:8000/api-auth/login/

API Logout (DRF)	http://127.0.0.1:8000/api-auth/logout/

Books API	http://127.0.0.1:8000/api/books/

Users API	http://127.0.0.1:8000/api/users/

Transactions API	http://127.0.0.1:8000/api/transactions/
 API Documentation
 Base URL
http://127.0.0.1:8000/


All endpoints are prefixed with /api/.

 Books Endpoints
Method	Endpoint	Description	Request Example	Response Example
GET	/api/books/	Retrieve all books	—	[{"id":1,"title":"Atomic Habits","author":"James Clear","isbn":"12345"}]
POST	/api/books/	Add a new book	{"title":"Atomic Habits","author":"James Clear","isbn":"12345","published_date":"2024-01-01","copies_available":5}	{"id":1,"title":"Atomic Habits",...}
GET	/api/books/{id}/	Retrieve one book	—	{"id":1,"title":"Atomic Habits",...}
PUT	/api/books/{id}/	Update book info	{"copies_available":4}	{"id":1,"copies_available":4}
DELETE	/api/books/{id}/	Delete a book	—	204 No Content
 Users Endpoints
Method	Endpoint	Description	Request Example	Response Example
GET	/api/users/	Retrieve all users	—	[{"id":1,"username":"mosi","email":"mosi@example.com"}]
POST	/api/users/	Create a new user	{"username":"mosi","email":"mosi@example.com"}	{"id":1,"username":"mosi",...}
GET	/api/users/{id}/	Retrieve user details	—	{"id":1,"username":"mosi",...}
PUT	/api/users/{id}/	Update user details	{"active":false}	{"id":1,"active":false}
DELETE	/api/users/{id}/	Delete user	—	204 No Content
 Transactions Endpoints
Method	Endpoint	Description	Request Example	Response Example
GET	/api/transactions/	List all transactions	—	[{"id":1,"user":1,"book":2,"checkout_date":"2025-11-01"}]
POST	/api/transactions/	Borrow a book	{"user":1,"book":2}	{"id":1,"user":1,"book":2,"checkout_date":"2025-11-01"}
PUT	/api/transactions/{id}/return/	Return a borrowed book	{"return_date":"2025-11-05"}	{"id":1,"return_date":"2025-11-05"}
 Authentication Endpoints
Method	Endpoint	Description
POST	/api-auth/login/	Log in a user
POST	/api-auth/logout/	Log out the authenticated user
 Notes

All API requests and responses are in JSON format.

Authentication is required for POST, PUT, and DELETE requests.

Anonymous users can only view public data (GET requests).

 Admin Dashboard

Visit the Django Admin panel at:
 http://127.0.0.1:8000/admin/

From here, you can manage:

Books

Users

Transactions