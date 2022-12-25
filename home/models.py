from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20, null=True)

    class Meta:
        verbose_name = 'Users'
        verbose_name_plural = 'Users'
        db_table = 'Users'


class Province(models.Model):
    province_id = models.AutoField(primary_key=True)
    province_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.province_name


class Cities(models.Model):
    city_id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=100, null=True)
    postal_code = models.CharField(max_length=15, null=True)
    type = models.CharField(max_length=50, null=True)
    province = models.ForeignKey(Province,  on_delete=models.CASCADE)

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name_plural = 'Cities'


class Shipment(models.Model):
    shipment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    city = models.ForeignKey(Cities, on_delete=models.CASCADE)
    courier = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.courier


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class SizeCategories(models.Model):
    size_category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Size Categories'


class Sizes(models.Model):
    size_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    product_size = models.CharField(max_length=100)
    size_category = models.ForeignKey(SizeCategories, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Sizes'


class Brands(models.Model):
    brand_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Brands'


class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()
    image = models.ImageField(upload_to='home/image_upload', null=True)
    desc = models.CharField(max_length=250)
    size = models.ForeignKey(Sizes, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brands, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Products'


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    unique_code = models.CharField(max_length=250, null=True, blank=True)
    status = models.BooleanField(default=False)
    quantity = models.IntegerField()
    date = models.DateField()
    price_total = models.FloatField()

    def __str__(self):
        return str(self.user)


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    unique_code = models.CharField(max_length=250)
    date = models.DateField()
    created_at = models.DateField()
    updated_at = models.DateField()
    gross_amount = models.IntegerField()
    status = models.BooleanField()

    def __str__(self):
        return self.order_id


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    store = models.CharField(max_length=100)
    gross_amount = models.IntegerField()
    payment_type = models.CharField(max_length=100)

    def __str__(self):
        return self.payment_type


class ProductPurchases(models.Model):
    product_purchases_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    supplier = models.CharField(max_length=150)
    stock = models.IntegerField()
    date = models.DateField()
    status = models.BooleanField()

    def __str__(self):
        return self.product

    class Meta:
        verbose_name_plural = 'Product Purchases'
