from django.test import TestCase

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from .models import User, Book, Transaction

class CheckoutReturnTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", email="a@example.com", password="password123")
        self.book = Book.objects.create(title="Django for Pros", author="A Author", isbn="1234567890123", copies_available=2)
        self.client = APIClient()
        resp = self.client.post("/api/auth/token/", {"username": "alice", "password": "password123"})
        self.token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_checkout_and_return(self):
        # checkout
        resp = self.client.post("/api/transactions/checkout/", {"book": self.book.id})
        self.assertEqual(resp.status_code, 201)
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, 1)

        # cannot checkout same book again by same user (unique active)
        resp = self.client.post("/api/transactions/checkout/", {"book": self.book.id})
        self.assertEqual(resp.status_code, 400)

        # return
        resp = self.client.post("/api/transactions/return_book/", {"book": self.book.id})
        self.assertEqual(resp.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, 2)

        # can checkout again
        resp = self.client.post("/api/transactions/checkout/", {"book": self.book.id})
        self.assertEqual(resp.status_code, 201)
