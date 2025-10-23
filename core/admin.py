from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Book, Transaction

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("date_of_membership", "is_active_member")}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Book)
admin.site.register(Transaction)