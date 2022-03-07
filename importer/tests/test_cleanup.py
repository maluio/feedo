from datetime import timedelta
from unittest import mock

from django.utils import timezone

import pytest

from importer.management.commands._cleanup import do_cleanup


@pytest.mark.django_db
def test_cleanup_non_updated(make_article):
    with mock.patch('core.models.get_now') as now:
        now.return_value = None
        a1 = make_article()
        a1.content = 'content1'
        a1.description = 'description1'
        a1.unread = False
        a1.saved = False
        a1.save()

    do_cleanup()

    a1.refresh_from_db()

    assert a1.content == ''
    assert a1.description == ''


@pytest.mark.django_db
def test_cleanup_old(make_article):
    today = timezone.now()
    with mock.patch('core.models.get_now') as now:
        now.return_value = today - timedelta(days=7)
        a1 = make_article()
        a1.content = 'content1'
        a1.description = 'description1'
        a1.unread = False
        a1.saved = False
        a1.save()

    do_cleanup()

    a1.refresh_from_db()

    assert a1.content == ''
    assert a1.description == ''


@pytest.mark.django_db
def test_cleanup_ignore_unread(make_article):
    with mock.patch('core.models.get_now') as now:
        now.return_value = None
        a1 = make_article()
        a1.content = 'content1'
        a1.description = 'description1'
        a1.unread = True
        a1.saved = False
        a1.save()

    do_cleanup()

    a1.refresh_from_db()

    assert a1.content == 'content1'
    assert a1.description == 'description1'


@pytest.mark.django_db
def test_cleanup_ignore_saved(make_article):
    with mock.patch('core.models.get_now') as now:
        now.return_value = None
        a1 = make_article()
        a1.content = 'content1'
        a1.description = 'description1'
        a1.unread = False
        a1.saved = True
        a1.save()

    do_cleanup()

    a1.refresh_from_db()

    assert a1.content == 'content1'
    assert a1.description == 'description1'
