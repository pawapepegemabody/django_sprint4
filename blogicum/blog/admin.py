from django.contrib import admin

from .models import Box, Order, Review, ServiceType


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'price',
        'slug',
        'is_published',
        'created_at'
    )


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'capacity',
        'is_published',
        'created_at'
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'car_model',
        'car_number',
        'client',
        'washer',
        'box',
        'service_type',
        'appointment_date',
        'status',
        'price',
        'discount',
        'is_published',
        'created_at'
    )
    list_filter = ('status', 'is_published', 'service_type', 'box')
    search_fields = ('car_model', 'car_number', 'client__username')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'rating',
        'order',
        'author',
        'created_at'
    )
