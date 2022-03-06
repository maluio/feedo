from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from core.models import Article
import logging

logger = logging.getLogger(__name__)


def do_cleanup():
    logger.info(f"Starting cleanup.")
    today = timezone.now()
    past_date = today - timedelta(days=7)
    articles = Article.objects.exclude(content__exact='').filter(unread=False).filter(saved=False).filter(
        Q(updated_at__lt=past_date) | Q(updated_at__isnull=True))
    for article in articles:
        logger.info(f"Cleaning article {article.id}")
        article.content = ''
        article.description = ''
        article.save()
