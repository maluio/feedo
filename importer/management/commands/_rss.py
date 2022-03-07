from django.utils.timezone import make_aware
from dateutil import parser

from core.models import Feed, Article
import feedparser

import logging

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

            if not can_import(f, item):
                continue

            article = Article()
            article.feed = f
            article.title = item["title"]
            article.link = item["link"]
            article.description = item.get("description", "")
            article.unread = True
            article.content = item.get("content", "")
            if "published" in item:
                article.published_at = parse_date(item["published"])
            article.save()


def can_import(feed: Feed, item) -> bool:
    # article already in DB ?
    if len(Article.objects.filter(link=item["link"])) > 0:
        return False

    if "filtered" in feed.extras:
        for word in feed.extras["filtered"]:
            if word.lower() in item["title"].lower():
                return False

    return True


def parse_date(value):
    try:
        parsed = parser.parse(value)
        # make timezone aware
        if not parsed.tzinfo:
            parsed = make_aware(parsed)
        return parsed
    except Exception as e:
        return None
