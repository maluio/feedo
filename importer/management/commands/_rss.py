from django.utils.timezone import make_aware
from dateutil import parser

from core.models import Feed, Article
import feedparser

import logging
import warnings

logger = logging.getLogger(__name__)


def do_import():
    logger.info("Starting rss import")
    feeds = Feed.objects_active.filter(type__exact=Feed.Type.RSS)
    for f in feeds:
        logger.info(f"Importing {f.title}")
        try:
            parsed_feed = feedparser.parse(f.external_uid)
        except Exception as e:
            logger.error(f"Error {e}")
            continue

        for item in parsed_feed.entries:

            article = Article()
            article.feed = f
            article.title = item["title"]
            article.link = item["link"]
            article.description = item.get("description", "")
            article.unread = True
            article.content = item.get("content", "")
            if "published" in item:
                article.published_at = parse_date(item["published"])
            if "rss" in parsed_feed.version and "guid" in item:
                article.guid = item["guid"]
            elif "atom" in parsed_feed.version and "id" in item:
                article.guid = item["id"]
            else:
                article.guid = item["link"]

            if can_import(f, article):
                article.save()


def can_import(feed: Feed, article: Article) -> bool:
    # article already in DB ?
    if len(Article.objects.filter(guid=article.guid)) > 0:
        return False
    if len(Article.objects.filter(link=article.link)) > 0:
        return False

    if "filtered" in feed.extras:
        for word in feed.extras["filtered"]:
            if word.lower() in article.title.lower():
                return False

    return True


def parse_date(value):
    try:
        # To ignore warning of type: "UnknownTimezoneWarning: tzname EST identified but not understood."
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            parsed = parser.parse(value)
        # make timezone aware
        if not parsed.tzinfo:
            parsed = make_aware(parsed)
        return parsed
    except Exception as e:
        return None
