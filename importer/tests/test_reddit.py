from unittest import mock
from unittest.mock import MagicMock, PropertyMock

from core.models import Article, Feed
from importer.management.commands._reddit import do_import as reddit_import
import pytest


@pytest.mark.django_db
def test_import(monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "123")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "123")
    monkeypatch.setenv("REDDIT_PASSWORD", "123")
    monkeypatch.setenv("REDDIT_USERNAME", "user1")

    with mock.patch(
        "importer.management.commands._reddit._get_reddit_client"
    ) as reddit_client:
        submission1 = MagicMock()
        type(submission1).permalink = PropertyMock(return_value="permalink-submission1")
        type(submission1).title = PropertyMock(return_value="title submission1")
        type(submission1).score = PropertyMock(return_value="100")
        type(submission1).created_utc = PropertyMock(return_value=1646668705)

        subreddit1 = MagicMock()
        subreddit1.top.return_value = [submission1]
        subreddit1.__str__.return_value = "subreddit1"

        reddit_obj = MagicMock()
        reddit_obj.user.subreddits.return_value = [subreddit1]
        reddit_client.return_value = reddit_obj

        # 1st run adds new feed + article
        reddit_import()

        feeds = Feed.objects.all()
        assert len(feeds) == 1
        assert feeds[0].title == "subreddit1"

        articles = Article.objects.all()
        assert len(articles) == 1
        assert articles[0].title == "title submission1 | [100]"

        # 2nd run of import doesn't add new feeds/articles
        reddit_import()

        feeds = Feed.objects.all()
        assert len(feeds) == 1
        assert feeds[0].title == "subreddit1"

        articles = Article.objects.all()
        assert len(articles) == 1
        assert articles[0].title == "title submission1 | [100]"


@pytest.mark.django_db
def test_import_ignore_inactive_feeds(monkeypatch, make_feed):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "123")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "123")
    monkeypatch.setenv("REDDIT_PASSWORD", "123")
    monkeypatch.setenv("REDDIT_USERNAME", "user1")

    feed = make_feed(type=Feed.Type.REDDIT, title="subreddit1")
    feed.active = False
    feed.save()

    with mock.patch("importer.management.commands._reddit.logger") as logger:
        with mock.patch(
            "importer.management.commands._reddit._get_reddit_client"
        ) as reddit_client:
            subreddit1 = MagicMock()
            subreddit1.top.return_value = []
            subreddit1.__str__.return_value = "subreddit1"

            reddit_obj = MagicMock()
            reddit_obj.user.subreddits.return_value = [subreddit1]
            reddit_client.return_value = reddit_obj

            reddit_import()

            logger.info.assert_called_with(
                "Subreddit subreddit1 not active. Aborting article import"
            )

            feeds = Feed.objects.all()
            assert len(feeds) == 1
            assert feeds[0].title == "subreddit1"

            articles = Article.objects.all()
            assert len(articles) == 0
