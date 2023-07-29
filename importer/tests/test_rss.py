import datetime
from datetime import tzinfo
from unittest import mock

from core.models import Article, Feed
from importer.management.commands._rss import do_import as do_rss_import

import pytest

atom_feed = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xml:base="http://example.org/"
      xml:lang="en">
    <title type="text">Sample Feed</title>
    <subtitle type="html">
        For documentation &lt;em&gt;only&lt;/em&gt;
    </subtitle>
    <link rel="alternate" href="/"/>
    <link rel="self"
          type="application/atom+xml"
          href="http://www.example.org/atom10.xml"/>
    <rights type="html">
        &lt;p>Copyright 2005, Mark Pilgrim&lt;/p>&lt;
    </rights>
    <id>tag:feedparser.org,2005-11-09:/docs/examples/atom10.xml</id>
    <generator
            uri="http://example.org/generator/"
            version="4.0">
        Sample Toolkit
    </generator>
    <updated>2005-11-09T11:56:34Z</updated>
    <entry>
        <title>First atom entry title</title>
        <link rel="alternate"
              href="/entry/3"/>
        <link rel="related"
              type="text/html"
              href="http://search.example.com/"/>
        <link rel="via"
              type="text/html"
              href="http://toby.example.com/examples/atom10"/>
        <link rel="enclosure"
              type="video/mpeg4"
              href="http://www.example.com/movie.mp4"
              length="42301"/>
        <id>entry/3</id>
        <published>2005-11-09T00:23:47Z</published>
        <updated>2005-11-09T11:56:34Z</updated>
        <summary type="text/plain" mode="escaped">Watch out for nasty tricks</summary>
        <content type="application/xhtml+xml" mode="xml"
                 xml:base="http://example.org/entry/3" xml:lang="en-US">
            <div xmlns="http://www.w3.org/1999/xhtml">Watch out for
                <span style="background: url(javascript:window.location='http://example.org/')">
                    nasty tricks
                </span>
            </div>
        </content>
    </entry>
</feed>
""".strip(
    "\n"
).strip()

rss_feed = """
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
    <channel>
        <title>Sample Feed</title>
        <description>For documentation &lt;em&gt;only&lt;/em&gt;</description>
        <link>http://example.org/</link>
        <pubDate>Sat, 07 Sep 2002 00:00:01 GMT</pubDate>
        <!-- other elements omitted from this example -->
        <item>
            <title>First rss entry title</title>
            <link>http://example.org/entry/{guid}</link>
            <description>Watch out for &lt;span style="background-image:
                url(javascript:window.location='http://example.org/')"&gt;nasty
                tricks&lt;/span&gt;
            </description>
            <pubDate>Thu, 05 Sep 2002 00:00:01 GMT</pubDate>
            <guid>{guid}</guid>
            <!-- other elements omitted from this example -->
        </item>
    </channel>
</rss>
""".strip(
    "\n"
).strip()


@pytest.mark.django_db
def test_import_atom(make_feed):
    feed = make_feed()
    feed.external_uid = atom_feed
    feed.save()

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 1

    assert articles[0].title == "First atom entry title"
    assert articles[0].link == "http://example.org/entry/3"
    assert articles[0].guid == "http://example.org/entry/3"


@pytest.mark.django_db
def test_import_rss(make_feed):
    feed = make_feed()
    feed.external_uid = rss_feed.format(guid='12345')
    feed.save()

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 1

    assert articles[0].title == "First rss entry title"
    assert articles[0].link == "http://example.org/entry/12345"
    assert articles[0].guid == "12345"
    assert articles[0].published_at == datetime.datetime(
        2002, 9, 5, 0, 0, 1, tzinfo=datetime.timezone.utc
    )


@pytest.mark.django_db
def test_import_only_once(make_feed):
    feed = make_feed()
    feed.external_uid = rss_feed.format(guid='12345')
    feed.save()

    feed.external_uid = rss_feed.format(guid='12345')
    feed.save()

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 1

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 1

    feed.external_uid = rss_feed.format(guid='54321')
    feed.save()

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 2


@pytest.mark.django_db
def test_import_ignore_filtered(make_feed):
    feed = make_feed()
    feed.extras = {"filtered": ["first"]}
    feed.external_uid = rss_feed
    feed.save()

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 0

    Feed.objects.all().delete()

    feed = make_feed()
    feed.extras = {"filtered": ["not_in_title"]}
    feed.external_uid = rss_feed
    feed.save()

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 1


@pytest.mark.django_db
def test_import_ignore_inactive_feeds(make_feed):
    feed = make_feed()
    feed.active = False
    feed.external_uid = rss_feed
    feed.save()

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 0


@pytest.mark.django_db
def test_import_continue_after_error(make_feed):
    feed = make_feed()
    feed.external_uid = "i am not a feed"
    feed.save()

    feed2 = make_feed()
    feed2.external_uid = rss_feed
    feed2.save()

    do_rss_import()
    articles = Article.objects.all()
    assert len(articles) == 1
