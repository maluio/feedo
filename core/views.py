import re
from urllib.parse import urlencode, quote

from dateutil import parser
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from .models import Article, Feed, Tag


class ArticlesSaved(ListView):
    model = Article
    queryset = Article.objects.filter(saved=True)
    template_name = "core/articles_saved_list.html"
    ordering = "-created_at"


def index(request):
    if request.GET.get("tag"):
        # remove non-numbers + non-letters :
        tag = re.sub(r"[\W_]+", "", request.GET.get("tag"))
        request.session["tag"] = tag
    elif request.session.get("tag"):
        tag = request.session.get("tag")
    else:
        tag = Feed.DEFAULT_TAG

    # check out https://docs.djangoproject.com/en/dev/topics/db/aggregation/#topics-db-aggregation
    feeds = Feed.objects.raw(
        f"""
        SELECT feed.*
        FROM core_feed as feed
                 INNER JOIN core_article as article ON (feed.id = article.feed_id)
        WHERE article.unread AND feed.active
        GROUP BY feed.id
    """
    )

    tags = Tag.objects.all()
    visible_feeds = []

    for feed in feeds:
        if tag in [t.name for t in feed.tags.all()]:
            visible_feeds.append(feed)
        count = feed.unread_count()
        for feed_tag in feed.tags.all():
            for tag_tag in tags:
                if tag_tag.id == feed_tag.id:
                    tag_tag.unread_article_count = tag_tag.unread_article_count + count

    context = {"unreadByFeed": visible_feeds, "tags": tags, "activeTag": tag}

    return render(request, "core/index.html", context)


def feed_articles(request, feed_id):
    articles = Article.objects.filter(feed__id=feed_id, unread=True).order_by(
        "created_at"
    )

    if len(articles) == 0:
        return HttpResponseRedirect(reverse("core:index"))

    context = {
        "articles": articles,
        "feed": Feed.objects.get(pk=feed_id),
        "last_created_at": quote(articles.last().created_at.isoformat()),
    }

    return render(request, "core/feed_articles.html", context)


def article_detail(request, article_id):
    article = Article.objects.get(id=article_id)
    feed = Feed.objects.get(id=article.feed_id)
    context = {"article": article, "feed": feed}
    return render(request, "core/article_detail.html", context)


def article_read(request, article_id):
    article = Article.objects.get(id=article_id)
    article.mark_read()
    article.save()
    return HttpResponse()


def article_save(request, article_id):
    article = Article.objects.get(id=article_id)
    article.saved = True
    article.save()

    return HttpResponse()


def article_read_all(request, feed_id):
    articles = Article.objects.filter(feed__id=feed_id, unread=True)
    if request.GET.get("last-created-at"):
        last_created = parser.parse(request.GET.get("last-created-at"))
        articles = articles.filter(created_at__lte=last_created)
    for article in articles:
        article.mark_read()
        article.save()

    return HttpResponseRedirect(reverse("core:forward_to_next_feed"))


def forward_to_next_feed(request):
    res = Feed.objects.raw(
        """
        SELECT feed.*
        FROM core_feed as feed
                INNER JOIN core_article as article ON (feed.id = article.feed_id)
                JOIN core_feed_tags cft on feed.id = cft.feed_id
                INNER JOIN core_tag ct on ct.id = cft.tag_id
        WHERE article.unread
          AND feed.active
        ORDER BY ct.position DESC
        LIMIT 1
    """
    )

    feed = None

    for row in res:
        feed = row
        break

    if not feed:
        return HttpResponseRedirect(reverse("core:index"))

    return HttpResponseRedirect(
        reverse("core:feed_articles", kwargs={"feed_id": feed.id})
    )
