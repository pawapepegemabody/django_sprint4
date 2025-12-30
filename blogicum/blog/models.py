from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class ServiceType(models.Model):
    title = models.CharField(
        'Название услуги',
        max_length=256
    )
    description = models.TextField('Описание')
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        )
    )
    is_published = models.BooleanField(
        'Доступно',
        default=True,
        help_text='Снимите галочку, чтобы скрыть услугу.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'тип услуги'
        verbose_name_plural = 'Типы услуг'

    def __str__(self):
        return self.title


class Box(models.Model):
    name = models.CharField(
        'Название бокса',
        max_length=256
    )
    capacity = models.PositiveIntegerField(
        'Вместимость (машин)',
        default=2
    )
    is_published = models.BooleanField(
        'Доступен',
        default=True,
        help_text='Снимите галочку, чтобы скрыть бокс.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'бокс'
        verbose_name_plural = 'Боксы'

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    car_model = models.CharField('Модель автомобиля', max_length=256)
    car_number = models.CharField('Гос. номер', max_length=20)
    description = models.TextField('Примечания', blank=True)
    appointment_date = models.DateTimeField(
        'Дата и время записи',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные записи.'
        )
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Клиент'
    )
    washer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        verbose_name='Мойщик',
        limit_choices_to={'is_staff': False}
    )
    box = models.ForeignKey(
        Box,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Бокс'
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Тип услуги'
    )
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    discount = models.DecimalField(
        'Скидка (%)',
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    car_image = models.ImageField(
        'Фото автомобиля',
        upload_to='cars',
        blank=True
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    is_published = models.BooleanField(
        'Активна',
        default=True,
        help_text='Снимите галочку, чтобы скрыть запись.'
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'Записи'
        ordering = ('-appointment_date',)

    def __str__(self):
        return f'{self.car_model} - {self.appointment_date}'

    def get_final_price(self):
        """Рассчитать итоговую цену с учетом скидки"""
        if self.price:
            discount_amount = self.price * (self.discount / 100)
            return self.price - discount_amount
        return None


class Review(models.Model):
    text = models.TextField('Текст отзыва')
    rating = models.PositiveIntegerField(
        'Оценка',
        choices=[(i, i) for i in range(1, 6)],
        default=5
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Запись'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('created_at',)

    def __str__(self):
        return f'Отзыв {self.author.username} на {self.order.car_model}'
