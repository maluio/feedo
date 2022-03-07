from core.models import Feed, Article, Tag
import pytest


@pytest.fixture
def make_tag():
    return _make_tag


def _make_tag(name='default') -> Tag:
    return Tag.objects.create(name=name)


@pytest.fixture
def make_feed():
    return _make_feed


def _make_feed(title="feed1", type=Feed.Type.RSS, external_uid="https://example.com/rss",
               with_default_tag=True) -> Feed:
    feed = Feed.objects.create(title=title, type=type, external_uid=external_uid)
    if with_default_tag:
        feed.tags.add(_make_tag())
        feed.save()
    return feed


@pytest.fixture
def make_article():
    def _make_article(title="article1", feed=None, link="https://example.com/article/1") -> Article:
        if not feed:
            feed = _make_feed()
        return Article.objects.create(title=title, feed=feed, link=link)

    return _make_article
