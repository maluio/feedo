# Generated by Django 3.1 on 2022-03-06 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_article_saved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='type',
            field=models.CharField(choices=[('RSS', 'Rss'), ('Reddit', 'Reddit'), ('Mail', 'Mail')], default='RSS', max_length=10),
        ),
    ]