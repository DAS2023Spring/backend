# Generated by Django 4.1.7 on 2023-06-13 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='header_image',
            field=models.ImageField(default=None, upload_to=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movie',
            name='imdb_rating',
            field=models.FloatField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movie',
            name='story',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
