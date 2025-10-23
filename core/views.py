from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Book, Transaction
from .serializers import UserSerializer, BookSerializer, TransactionSerializer
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Registration is open; restrict as needed

    def get_permissions(self):
        if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        # Optionally restrict list to staff, but for now allow retrieval by id if authenticated
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk) if self.request.user.is_authenticated else User.objects.none()


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("title")
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly := getattr(__import__("rest_framework.permissions"), "IsAuthenticatedOrReadOnly")]

    def get_queryset(self):
        qs = Book.objects.all().order_by("title")
        # Filters: availability, title, author, isbn
        available = self.request.query_params.get("available")
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")
        isbn = self.request.query_params.get("isbn")

        if available is not None:
            if available.lower() in ("1", "true", "yes"):
                qs = qs.filter(copies_available__gt=0)
            elif available.lower() in ("0", "false", "no"):
                qs = qs.filter(copies_available__lte=0)

        if title:
            qs = qs.filter(title__icontains=title)
        if author:
            qs = qs.filter(author__icontains=author)
        if isbn:
            qs = qs.filter(isbn__icontains=isbn)
        return qs


class TransactionViewSet(viewsets.GenericViewSet):
    queryset = Transaction.objects.all().select_related("book", "user")
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # list user's transactions (history)
        qs = self.queryset.filter(user=request.user).order_by("-checkout_date")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TransactionSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """
        Checkout a book:
        POST payload: {"book": <book_id>}
        """
        serializer = TransactionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        tx = serializer.save()
        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def return_book(self, request):
        """
        Return a checked-out book:
        POST payload: {"book": <book_id>}
        """
        book_id = request.data.get("book")
        if not book_id:
            return Response({"detail": "book id required"}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            # find active transaction
            tx_qs = Transaction.objects.select_for_update().filter(user=request.user, book_id=book_id, return_date__isnull=True)
            tx = tx_qs.first()
            if not tx:
                return Response({"detail": "No active checkout for this user and book."}, status=status.HTTP_400_BAD_REQUEST)

            # mark returned
            tx.status = Transaction.STATUS_RETURNED
            tx.return_date = timezone.now()
            tx.save()

            # increment copies
            book = Book.objects.select_for_update().get(pk=book_id)
            book.copies_available = book.copies_available + 1
            book.save()

        return Response(TransactionSerializer(tx).data, status=status.HTTP_200_OK)
