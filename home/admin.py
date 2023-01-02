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
    list_display = ("city_id", "province", "address", "city_name",
                    "postal_code")


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("shipment_id", "product_order",
                    "user", "city", "courier")


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "price", "stock", "desc",
                    "size", "brand", "category", "image")


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
    list_display = ("cart_id", "product", "user",
                    "quantity", "date", "price_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "product", "quantity", "user", "unique_code",
                    "created_at", "updated_at", "gross_amount", "status")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "order", "transaction_time",
                    "gross_amount", "payment_type")


@admin.register(ProductPurchases)
class ProductPurchasesAdmin(admin.ModelAdmin):
    list_display = ("product_purchases_id", "user", "product",
                    "supplier", "stock", "date", "status")


@admin.register(RefundProduct)
class RefundProductAdmin(admin.ModelAdmin):
    list_display = ("refund_id", "order", "price", "reason")
