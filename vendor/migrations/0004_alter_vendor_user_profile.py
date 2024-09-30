# Generated by Django 5.1.1 on 2024-09-30 04:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_role'),
        ('vendor', '0003_alter_vendor_vendor_license'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='user_profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to='accounts.userprofile'),
        ),
    ]