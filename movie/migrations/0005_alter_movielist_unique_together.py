# Generated by Django 4.1.7 on 2023-06-14 12:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movie', '0004_alter_movierating_options'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='movielist',
            unique_together={('user', 'name')},
        ),
    ]
