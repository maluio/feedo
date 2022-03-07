from datetime import datetime
from django.utils.timezone import make_aware

from praw import Reddit
import os

from core.models import Feed, Article
import logging

logger = logging.getLogger(__name__)


def _get_reddit_client():
    user_agent = "testscript by /u/{}".format(os.getenv('REDDIT_USERNAME'))
    return Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                  client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                  password=os.getenv('REDDIT_PASSWORD'),
                  user_agent=user_agent,
                  username=os.getenv('REDDIT_USERNAME')
                  )


def do_import():
    logger.info('Starting reddit import')
    reddit = _get_reddit_client()
    for sr in reddit.user.subreddits():
        sr_title = "{}".format(sr)
        logger.info(f'Importing subreddit {sr_title}')
        if len(Feed.objects.filter(title=sr_title)) == 0:
            feed = Feed()
            feed.title = sr_title
            feed.external_uid = "reddit.com/{}".format(sr_title)
            feed.type = Feed.Type.REDDIT
            feed.save()
        else:
            feed = Feed.objects_active.filter(title=sr_title).first()
        if not feed:
            logger.info(f'Subreddit {sr_title} not active. Aborting article import')
            continue
        for submission in sr.top(time_filter='day', limit=15):
            link = "https://old.reddit.com{}".format(submission.permalink)
            if len(Article.objects.filter(link=link)) > 0:
                continue

            article = Article()
            article.feed = feed
            article.link = link
            article.title = "{} | [{}]".format(submission.title, submission.score)
            article.content = ''
            article.published_at = make_aware(datetime.fromtimestamp(submission.created_utc))
            article.save()
