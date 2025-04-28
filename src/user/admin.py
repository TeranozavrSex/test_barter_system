from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from django.contrib.auth.apps import AuthConfig
from django.contrib.auth.models import Group

from .models import AccessGroup, CustomUser, ErrorLog

AuthConfig.verbose_name = "Django Пользователи"
admin.site.unregister(Group)


class CustomUserAdmin(OriginalUserAdmin):
    list_display = [
        "username",
        "email",
        "tg_id",
        "first_name",
        "last_name",
        "is_superuser",
    ]
    readonly_fields = ["tg_id", "token_hash", "token_created_at"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Персональная информация",
            {
                "fields": (
                    "first_name",
                    "photo_url",
                    "last_name",
                    "email",
                    "tg_id",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    ordering = [
        "email",
        "tg_id",
        "first_name",
        "last_name",
    ]


class AccessGroupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
    ]
    fields = [
        "name",
        "description",
    ]


class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ["description", "created_at"]
    readonly_fields = ["description", "created_at"]


admin.site.register(ErrorLog, ErrorLogAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AccessGroup, AccessGroupAdmin)
