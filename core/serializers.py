from rest_framework import serializers
from django.db import transaction
from .models import User, Book, Transaction
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "date_of_membership", "is_active_member"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "isbn", "published_date", "copies_available"]

    def validate_isbn(self, value):
        # Basic validation: ensure unique ISBN (DB unique constraint will also prevent duplicates)
        qs = Book.objects.filter(isbn=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Book with this ISBN already exists.")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Transaction
        fields = ["id", "user", "book", "checkout_date", "return_date", "status"]

    def create(self, validated_data):
        """
        Create a checkout transaction:
        - Use select_for_update to lock the Book row to avoid race conditions.
        - Ensure copies_available > 0
        - Create transaction and decrement copies_available atomically.
        """
        request = self.context.get("request")
        user = request.user
        book = validated_data["book"]

        with transaction.atomic():
            # lock the book row
            locked_book = Book.objects.select_for_update().get(pk=book.pk)
            if locked_book.copies_available <= 0:
                raise serializers.ValidationError("No copies available for checkout.")
            # check unique active constraint handled by DB; but raise friendly error
            active_exists = Transaction.objects.filter(user=user, book=locked_book, return_date__isnull=True).exists()
            if active_exists:
                raise serializers.ValidationError("You already have an active checkout for this book.")
            # decrement
            locked_book.copies_available = locked_book.copies_available - 1
            locked_book.save()

            tx = Transaction.objects.create(user=user, book=locked_book, status=Transaction.STATUS_CHECKED_OUT)
            return tx