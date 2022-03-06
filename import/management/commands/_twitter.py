import datetime
import json
import os
from typing import List
from dateutil.parser import parse

import requests
from pydantic import BaseModel
from requests import Timeout

from core.models import Feed, Article

import logging

logger = logging.getLogger(__name__)


class Tweet(BaseModel):
    id: int
    created_at: datetime.datetime
    hashtags: List[str]
    link: str
    tweet: str
    likes_count: int
    name: str
    replies_count: int
    retweets_count: int
    thumbnail: str


def do_import():
    twipeater = os.getenv('TWIPEATER_URL', 'http://twipeater')
    for f in Feed.objects_active.filter(type=Feed.Type.TWITTER):
        logger.info(f'Importing tweets for username {f.extras["username"]}')
        try:
            r = requests.get(f'{twipeater}/tweets?username={f.extras["username"]}', timeout=5)
            r.raise_for_status()
        except Timeout:
            logger.error(f'Twipeater timed out for username {f.extras["username"]}')
            continue
        except Exception as e:
            logger.error(f'Twipeater returned error for username {f.extras["username"]}: {e}')
            continue
        content = json.loads(r.content)
        for t in content['data']:
            t['created_at'] = parse(t['created_at'])
            tw = Tweet(**t)
            if can_import(tw):
                a = Article()
                a.feed = f
                a.link = tw.link
                a.title = f'[{tw.likes_count}] {tw.tweet[0:20]}'
                a.description = tw.tweet
                a.content = tw.tweet
                a.published_at = tw.created_at
                a.image = tw.thumbnail
                a.save()


def can_import(tweet: Tweet) -> bool:
    # article already in DB ?
    if len(Article.objects.filter(link=tweet.link)) > 0:
        return False

    return True
