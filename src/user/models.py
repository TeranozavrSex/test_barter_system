# from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    tg_id = models.CharField(
        max_length=20,
        editable=False,
        unique=True,
        null=True,
        default=None,
    )
    photo_url = models.CharField(
        max_length=500,
        verbose_name="Ссылка на фото",
        null=True,
        blank=True,
        default=None,
    )
    token_hash = models.CharField(
        max_length=300, verbose_name="Token", null=True, default=None
    )
    token_created_at = models.DateTimeField(
        verbose_name="Token created at", null=True, default=None
    )

    def __str__(self):
        return self.email

    class Meta(AbstractUser.Meta):
        verbose_name = "Кастомные пользователи"
        verbose_name_plural = "Кастомные пользователи"


class AccessGroup(Group):
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class ErrorLog(models.Model):
    description = models.TextField(max_length=2048, verbose_name="Описание ошибки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        verbose_name = "Лог ошибки"
        verbose_name_plural = "Логи ошибок"
