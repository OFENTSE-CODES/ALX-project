from django.db import models

from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model to include membership date and active status.
    Username and email uniqueness are handled by AbstractUser but we ensure email optional uniqueness below if needed.
    """
    email = models.EmailField(unique=True)
    date_of_membership = models.DateField(default=timezone.now)
    is_active_member = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)  # ISBN-10/13, unique constraint
    published_date = models.DateField(null=True, blank=True)
    copies_available = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.title} by {self.author} ({self.isbn})"


class Transaction(models.Model):
    """
    Tracks checkout and return transactions.
    - When return_date is NULL => currently checked out
    - Enforce at-most-one active checkout per (user, book)
    """
    STATUS_CHECKED_OUT = "checked_out"
    STATUS_RETURNED = "returned"
    STATUS_CHOICES = [
        (STATUS_CHECKED_OUT, "Checked Out"),
        (STATUS_RETURNED, "Returned"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="transactions")
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CHECKED_OUT)

    class Meta:
        # prevent multiple active (non-returned) transactions for same user-book
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                condition=models.Q(return_date__isnull=True),
                name="unique_active_user_book"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.book} [{self.status}]"

    def mark_returned(self):
        if self.status != self.STATUS_RETURNED:
            self.status = self.STATUS_RETURNED
            self.return_date = timezone.now()
            self.save()
