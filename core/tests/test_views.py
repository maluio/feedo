import pytest
from urllib.parse import quote


@pytest.mark.django_db
def test_index_default_tag(client, make_article):
    make_article()

    r = client.get("/")

    context = r.context

    assert len(context["unreadByFeed"]) == 1
    assert context["activeTag"] == "default"
    assert context["tags"][0].name == "default"

    r = client.get("/?tag=not-existing-tag")

    context = r.context

    assert len(context["unreadByFeed"]) == 0
    assert context["activeTag"] == "notexistingtag"

    session = client.session
    session["tag"] = "session-tag"
    session.save()

    r = client.get("/")

    context = r.context

    assert len(context["unreadByFeed"]) == 0
    assert context["activeTag"] == "session-tag"


@pytest.mark.django_db
def test_unread_article_count(client, make_article, make_feed, make_tag):
    tag_non_default = make_tag(name="non-default")
    feed1 = make_feed(with_default_tag=False)
    feed1.tags.add(tag_non_default)
    feed1.save()
    make_article(feed=feed1)

    r = client.get("/")

    context = r.context

    assert len(context["unreadByFeed"]) == 0
    assert context["activeTag"] == "default"
    assert context["tags"][0].name == "non-default"
    assert context["tags"][0].unread_article_count == 1


@pytest.mark.django_db
def test_articles_by_feed(client, make_feed, make_article):
    feed1 = make_feed()
    r = client.get(f"/feeds/{feed1.id}/articles/", follow=False)
    assert r.status_code == 302
    assert r.url == "/"

    article1 = make_article(feed=feed1)

    r = client.get(f"/feeds/{feed1.id}/articles/", follow=False)
    assert r.status_code == 200
    assert len(r.context["articles"]) == 1
    # @todo : hard code expected date
    assert r.context["last_created_at"] == quote(article1.created_at.isoformat())


@pytest.mark.django_db
def test_article_detail(client, make_article):
    article1 = make_article(title="article1")

    r = client.get("/articles/1")

    article = r.context["article"]

    assert article.title == "article1"


@pytest.mark.django_db
def test_article_read(client, make_article):
    make_article(title="article1")

    response = client.get("/")
    articles = response.context["unreadByFeed"]

    assert len(articles) == 1

    client.get("/articles/1/read")

    response = client.get("/")
    articles = response.context["unreadByFeed"]

    assert len(articles) == 0


@pytest.mark.django_db
def test_article_read_all(client, make_feed, make_article):
    feed = make_feed()
    make_article(title="article1", feed=feed)
    make_article(title="article2", feed=feed, link="12345")

    response = client.get("/")
    feeds = response.context["unreadByFeed"]
    assert feeds[0].unread_count() == 2

    client.get("/articles/1/read-all")
    response = client.get("/")
    feeds = response.context["unreadByFeed"]

    assert len(feeds) == 0

    # @todo: test last-created-at


@pytest.mark.django_db
def test_article_save(client, make_article):
    make_article(title="article1")

    r = client.get("/articles/1/save")

    r = client.get("/articles/saved")
    articles = r.context["object_list"]

    assert len(articles) == 1
    assert articles[0].title == "article1"


@pytest.mark.django_db
def test_next_unread_article_by_feed(client, make_feed, make_article):
    make_feed(title="feed1")
    feed2 = make_feed(title="feed2", external_uid="12345")
    make_article(feed=feed2)
    make_feed(title="feed3", external_uid="1010")

    response = client.get("/feeds/forward-to-next-feed")

    assert response.status_code == 302
    assert response.url == "/feeds/2/articles/"


@pytest.mark.django_db
def test_next_unread_article_by_tag_position(client, make_tag, make_feed, make_article):
    tag1 = make_tag(name="tag1")
    tag1.position = 1
    tag1.save()

    tag2 = make_tag(name="tag2")
    tag2.position = 3
    tag2.save()

    tag3 = make_tag(name="tag3")
    tag3.position = 2
    tag3.save()

    feed1 = make_feed(title="feed1", with_default_tag=False)
    feed1.tags.add(tag1)
    feed1.save()

    feed2 = make_feed(title="feed2", external_uid="12345", with_default_tag=False)
    feed2.tags.add(tag2)
    feed2.save()

    feed3 = make_feed(title="feed2", external_uid="101010", with_default_tag=False)
    feed3.tags.add(tag3)
    feed3.save()

    make_article(feed=feed1)
    make_article(feed=feed2, link="12334")
    make_article(feed=feed3, link="10101")

    response = client.get("/feeds/forward-to-next-feed")

    assert response.status_code == 302
    assert response.url == "/feeds/2/articles/"
