from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import *
from django.template import loader
from django.http import HttpResponse
# Register your models here.


admin.site.unregister(Group)


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Additional Info',
            {
                'fields': (
                    'full_name',
                    'phone_number',
                    'address',
                    'city',
                    'province',
                    'zip_code',
                    'country',
                )
            }
        )
    )
    list_display = ('user_id', 'first_name', 'last_name', 'full_name', 'phone_number', 'email', 'is_active')


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("shipment_id", "product_order",
                    "user", "city", "service",
                    "description", "cost", "etd")

    def has_add_permission(self, request, obj=None):
        return False


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

    def has_add_permission(self, request, obj=None):
        return False


def export_report(queryset):
    order = []
    for item in queryset:

        try:
            payment = Payment.objects.get(order=item.order_id)
        except Payment.DoesNotExist:
            payment = '-'

        order.append(
            {
                'order_id': item.order_id,
                'product__name': item.product,
                'user__username': item.user.full_name,
                'quantity': item.quantity,
                'payment__transaction_time': payment.transaction_time if not isinstance(payment, str) else payment,
                'gross_amount': item.gross_amount,
                'payment__payment_type': payment.payment_type if not isinstance(payment, str) else payment,
                'status': item.status
            }
        )
    return order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "get_alamat", "get_phone", "product", "quantity",
                    "created_at", "gross_amount", "status", "verified")

    search_fields = ['created_at']

    @admin.display(ordering='user__user_id', description='Address')
    def get_alamat(self, obj):
        return f"{obj.user.address}, {obj.user.city}, {obj.user.province}"

    @admin.display(ordering='user__phone_number', description='Phone')
    def get_phone(self, obj):
        return f"{obj.user.phone_number}"

    def has_add_permission(self, request, obj=None):
        return False

    actions = ['export_pdf', 'export_excel']

    def export_pdf(self, request, queryset):
        context = {}
        order = export_report(queryset)

        load_template = 'report/cetak-laporan-penjualan.html'

        context['order'] = order
        context['segment'] = load_template

        html_template = loader.get_template(load_template)

        return HttpResponse(html_template.render(context, request))

    export_pdf.short_description = "Cetak PDF Order yang dipilih"

    def export_excel(self, request, queryset):
        context = {}
        order = export_report(queryset)

        load_template = 'report/export-excel.html'

        context['order'] = order
        context['segment'] = load_template

        html_template = loader.get_template(load_template)

        return HttpResponse(html_template.render(context, request))

    export_excel.short_description = "Cetak Excel Order yang dipilih"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "order", "transaction_time",
                    "gross_amount", "payment_type")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ProductPurchases)
class ProductPurchasesAdmin(admin.ModelAdmin):
    list_display = ("product_purchases_id", "user", "product",
                    "supplier", "stock", "date", "status")


@admin.register(RefundProduct)
class RefundProductAdmin(admin.ModelAdmin):
    list_display = ("refund_id", "order", "price", "reason")
