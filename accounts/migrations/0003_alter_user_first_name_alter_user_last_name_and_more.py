# Generated by Django 5.1.1 on 2024-10-01 03:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=50, validators=[django.core.validators.RegexValidator('^[a-zA-Z\\s]', 'Enter a Valid name (Only alphabets and spaces)')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=50, validators=[django.core.validators.RegexValidator('^[a-zA-Z\\s]', 'Enter a Valid name (Only alphabets and spaces)')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9_]+$', 'Usernames can only contain letters, numbers and underscores.')]),
        ),
    ]
