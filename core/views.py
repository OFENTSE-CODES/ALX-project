from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Book, Transaction
from .serializers import UserSerializer, BookSerializer, TransactionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def available(self, request):
        available_books = Book.objects.filter(copies_available__gt=0)
        serializer = self.get_serializer(available_books, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        user = request.user
        book_id = request.data.get("book_id")

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        if book.copies_available <= 0:
            return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already has this book
        if Transaction.objects.filter(user=user, book=book, return_date__isnull=True).exists():
            return Response({"error": "You already have this book checked out."}, status=status.HTTP_400_BAD_REQUEST)

        # Checkout
        Transaction.objects.create(user=user, book=book)
        book.copies_available -= 1
        book.save()
        return Response({"message": "Book checked out successfully!"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def return_book(self, request):
        user = request.user
        book_id = request.data.get("book_id")

        try:
            transaction = Transaction.objects.get(user=user, book_id=book_id, return_date__isnull=True)
        except Transaction.DoesNotExist:
            return Response({"error": "No active checkout found for this book"}, status=status.HTTP_400_BAD_REQUEST)

        transaction.return_date = models.DateField().to_python("today")
        transaction.save()

        book = transaction.book
        book.copies_available += 1
        book.save()

        return Response({"message": "Book returned successfully!"}, status=status.HTTP_200_OK)