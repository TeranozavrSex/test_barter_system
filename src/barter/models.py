from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import CustomUser


class Ad(models.Model):
    class Condition(models.TextChoices):
        NEW = 'new', _('Новый')
        USED = 'used', _('Б/у')
        BROKEN = 'broken', _('Требует ремонта')

    class Category(models.TextChoices):
        ELECTRONICS = 'electronics', _('Электроника')
        CLOTHING = 'clothing', _('Одежда')
        BOOKS = 'books', _('Книги')
        FURNITURE = 'furniture', _('Мебель')
        OTHER = 'other', _('Другое')

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name=_('Пользователь')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Заголовок')
    )
    description = models.TextField(
        verbose_name=_('Описание')
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('URL изображения')
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name=_('Категория')
    )
    condition = models.CharField(
        max_length=20,
        choices=Condition.choices,
        default=Condition.USED,
        verbose_name=_('Состояние')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активно')
    )

    class Meta:
        verbose_name = _('Объявление')
        verbose_name_plural = _('Объявления')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class ExchangeProposal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Ожидает')
        ACCEPTED = 'accepted', _('Принято')
        REJECTED = 'rejected', _('Отклонено')
        CANCELLED = 'cancelled', _('Отменено')

    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='sent_proposals',
        verbose_name=_('Объявление отправителя')
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='received_proposals',
        verbose_name=_('Объявление получателя')
    )
    comment = models.TextField(
        verbose_name=_('Комментарий'),
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Статус')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Предложение обмена')
        verbose_name_plural = _('Предложения обмена')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['ad_sender', 'ad_receiver'],
                name='unique_exchange_proposal'
            )
        ]

    def __str__(self):
        return f"Предложение обмена #{self.id} ({self.get_status_display()})"
