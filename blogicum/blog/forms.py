from django import forms
from django.contrib.auth import get_user_model

from .models import Box, Order, Review, ServiceType

User = get_user_model()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'car_model',
            'car_number',
            'description',
            'appointment_date',
            'box',
            'service_type',
            'car_image'
        )
        widgets = {
            'appointment_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M:%S',
                attrs={'type': 'datetime-local'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service_type'].queryset = ServiceType.objects.filter(
            is_published=True
        )
        self.fields['box'].queryset = Box.objects.filter(
            is_published=True
        )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('text', 'rating')


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
