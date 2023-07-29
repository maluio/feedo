# Generated by Django 3.1 on 2022-05-21 07:38
import uuid

from django.db import migrations


def gen_guid(apps, schema_editor):
    Article = apps.get_model('core', 'Article')
    for row in Article.objects.all():
        row.guid = row.link
        row.save(update_fields=['guid'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0017_article_guid'),
    ]

    operations = [
        migrations.RunPython(gen_guid, reverse_code=migrations.RunPython.noop),
    ]