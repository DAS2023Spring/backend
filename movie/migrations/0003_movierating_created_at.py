# Generated by Django 4.1.7 on 2023-06-14 07:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0002_movie_header_image_movie_imdb_rating_movie_story'),
    ]

    operations = [
        migrations.AddField(
            model_name='movierating',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
