# Generated by Django 5.1.3 on 2024-12-05 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_movie_poster_url_movie_trailer_url_movie_year_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='description',
            new_name='synopsis',
        ),
    ]
