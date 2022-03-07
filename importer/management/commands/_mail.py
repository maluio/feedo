import os

from imap_tools import MailBox

from core.models import Feed, Article
import logging

logger = logging.getLogger(__name__)

imap_host = os.getenv('IMAP_HOST')
imap_user = os.getenv('IMAP_USER')
imap_pass = os.getenv('IMAP_PASSWORD')


def do_import():
    logger.info('Starting mail import')
    # https://github.com/ikvk/imap_tools
    with MailBox(imap_host).login(imap_user, imap_pass) as mailbox:
        for msg in mailbox.fetch():
            feed_id = f"mail_{imap_user}_{msg.from_}"
            logger.info(f'Importing {feed_id}')
            # feed already in DB ?
            if len(Feed.objects.filter(external_uid=feed_id)) == 0:
                feed = Feed()
                feed.title = msg.from_values.get('name')
                feed.external_uid = feed_id
                feed.type = Feed.Type.MAIL
                feed.save()
            else:
                feed = Feed.objects.filter(external_uid=feed_id)[0]

            article_key = f"mail_article_{imap_user}_{msg.uid}"

            # mark mail as seen
            mailbox.seen([msg.uid], True)
            # delete mail
            mailbox.delete([msg.uid])

            if not feed.active:
                logger.info(f'Mail feed {feed.title} not active. Aborting article import')
                continue

            # article already in DB ?
            if len(Article.objects.filter(link=article_key)) > 0:
                continue
            article = Article()
            article.feed = feed
            article.title = msg.subject
            article.description = msg.subject
            article.content = msg.text.replace("\n", "<br />\n")
            article.link = article_key
            article.save()
