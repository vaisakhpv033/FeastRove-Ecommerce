# Generated by Django 5.1.1 on 2024-09-29 09:34

import vendor.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='vendor_license',
            field=models.FileField(upload_to=vendor.models.vendor_license_path, validators=[vendor.models.validate_file_mimetype]),
        ),
    ]