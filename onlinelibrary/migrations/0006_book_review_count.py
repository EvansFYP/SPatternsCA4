# Generated by Django 5.0.1 on 2025-04-14 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinelibrary', '0005_userprofile_loyalty_count_alter_book_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='review_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
