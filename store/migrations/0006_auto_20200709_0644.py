# Generated by Django 3.0.8 on 2020-07-09 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_customer_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(),
        ),
    ]
