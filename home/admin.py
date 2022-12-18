from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Additional Info',
            {
                'fields': (
                    'full_name',
                    'phone_number',
                )
            }
        )
    )
    list_display = ('user_id', 'full_name', 'phone_number', 'email')


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("province_id", "province_name")


@admin.register(Cities)
class CitiesAdmin(admin.ModelAdmin):
    list_display = ("city_id", "province_id", "city_name",
                    "postal_code", "type")


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("shipment_id", "user_id", "city_id",
                    "courier")


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "price", "stock", "desc",
                    "size_id", "brand_id", "category_id")


@admin.register(Categories)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "name")


@admin.register(Sizes)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("size_id", "name", "product_size")


@admin.register(SizeCategories)
class SizeCategoriesAdmin(admin.ModelAdmin):
    list_display = ("size_category_id", "name")


@admin.register(Brands)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("brand_id", "name")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_id", "product_id", "user_id", "unique_code", "status",
                    "quantity", "date", "price_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "unique_code", "date", "created_at", "updated_at",
                    "gross_amount", "status")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "order_id", "store",
                    "gross_amount", "payment_type")


@admin.register(ProductPurchases)
class ProductPurchasesAdmin(admin.ModelAdmin):
    list_display = ("product_purchases_id", "user_id", "product_id",
                    "supplier", "stock", "date", "status")
