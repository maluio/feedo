# Generated by Django 3.1 on 2022-05-23 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20220521_0738'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='article',
            constraint=models.UniqueConstraint(fields=('feed', 'guid'), name='feed_guid'),
        ),
    ]