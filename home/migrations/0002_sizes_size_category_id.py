# Generated by Django 4.1.4 on 2022-12-18 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sizes',
            name='size_category_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.sizecategories'),
        ),
    ]
