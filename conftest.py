from core.models import Feed
import pytest


@pytest.fixture
def make_feed():
    return _make_feed


def _make_feed(title="feed1", type=Feed.Type.RSS, external_uid="https://example.com/rss") -> Feed:
    return Feed.objects.create(title=title, type=type, external_uid=external_uid)
