# Generated by Django 3.1.6 on 2021-03-06 04:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_feed_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="feed",
            name="rss_import",
        ),
    ]
