# Generated by Django 5.1.1 on 2024-10-04 11:16

import accounts.validators
import menu.models
import menu.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='image',
            field=models.ImageField(upload_to=menu.models.food_image_upload_path, validators=[accounts.validators.validate_file_mimetype]),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[menu.validators.validate_positive_price]),
        ),
    ]
