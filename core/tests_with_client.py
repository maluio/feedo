from django.test import TestCase, Client

from core.models import Article, Feed, Tag


class ArticleTest(TestCase):

    def test_list_unread_article(self):
        ta1 = Tag()
        ta1.position = 1
        ta1.name = 'default'
        ta1.save()

        f = Feed()
        f.title = 'f1'
        f.type = Feed.Type.RSS
        f.external_uid = '12345'
        f.save()

        f.tags.add(ta1)
        f.save()

        a = Article()
        a.content = 'content1'
        a.title = 'title1'
        a.description = 'description1'
        a.feed = f
        a.save()

        c = Client()
        response = c.get('/')
        articles = response.context['unreadByFeed']

        self.assertEqual(len(articles), 1)

    def test_article_for_feed(self):
        f = Feed()
        f.title = 'f1'
        f.type = Feed.Type.RSS
        f.external_uid = '12345'
        f.save()

        c = Client()
        response = c.get('/feeds/1/articles/')
        self.assertRedirects(response, '/')

        a = Article()
        a.content = 'content1'
        a.title = 'title1'
        a.description = 'description1'
        a.feed = f
        a.save()

        c = Client()

        response = c.get('/feeds/1/articles/')
        article = response.context['articles'][0]
        feed = response.context['feed']

        self.assertEqual('f1', feed.title)
        self.assertEqual('title1', article.title)

    def test_next_unread_article_by_feed(self):
        ta1 = Tag()
        ta1.name = 'tag1'
        ta1.save()

        f1 = Feed()
        f1.title = 'f1'
        f1.type = Feed.Type.RSS
        f1.external_uid = '12345'
        f1.save()

        f1.tags.add(ta1)
        f1.save()

        f2 = Feed()
        f2.title = 'f2'
        f2.type = Feed.Type.RSS
        f2.external_uid = 'abcdef'
        f2.save()

        f2.tags.add(ta1)
        f2.save()

        a = Article()
        a.content = 'content1'
        a.title = 'title1'
        a.description = 'description1'
        a.feed = f2
        a.save()

        c = Client()
        response = c.get('/feeds/forward-to-next-feed')

        self.assertRedirects(response, '/feeds/2/articles/')

    def test_next_unread_article_by_tag_position(self):
        ta1 = Tag()
        ta1.position = 1
        ta1.name = 'tag1'
        ta1.save()

        ta2 = Tag()
        ta2.position = 2
        ta2.name = 'tag2'
        ta2.save()

        f1 = Feed()
        f1.title = 'f1'
        f1.type = Feed.Type.RSS
        f1.external_uid = '12345'
        f1.save()

        f1.tags.add(ta1)
        f1.save()

        f2 = Feed()
        f2.title = 'f2'
        f2.type = Feed.Type.RSS
        f2.external_uid = 'abcdef'
        f2.save()

        f2.tags.add(ta2)
        f2.save()

        a1 = Article()
        a1.content = 'content1'
        a1.title = 'title1'
        a1.description = 'description1'
        a1.link = 'abc'
        a1.feed = f1
        a1.save()

        a2 = Article()
        a2.content = 'content2'
        a2.title = 'title2'
        a2.description = 'description2'
        a2.link = 'def'
        a2.feed = f2
        a2.save()

        c = Client()
        response = c.get('/feeds/forward-to-next-feed')

        self.assertRedirects(response, '/feeds/2/articles/')

    def test_save_article(self):
        f = Feed()
        f.title = 'f1'
        f.type = Feed.Type.RSS
        f.external_uid = '12345'
        f.save()

        a = Article()
        a.content = 'content1'
        a.title = 'title1'
        a.description = 'description1'
        a.feed = f
        a.saved = False
        a.save()

        c = Client()
        c.get('/articles/1/save')

        response = c.get('/articles/saved')
        articles = response.context['object_list']

        self.assertEqual(len(articles), 1)
        self.assertEqual('title1', articles[0].title)

    def test_article_detail(self):
        ta1 = Tag()
        ta1.position = 1
        ta1.name = 'default'
        ta1.save()

        f = Feed()
        f.title = 'f1'
        f.type = Feed.Type.RSS
        f.external_uid = '12345'
        f.save()

        f.tags.add(ta1)
        f.save()

        a = Article()
        a.content = 'content1'
        a.title = 'title1'
        a.description = 'description1'
        a.feed = f
        a.unread = True
        a.save()

        c = Client()

        response = c.get('/articles/1')
        article = response.context['article']

        self.assertEqual('title1', article.title)

    def test_read_article(self):
        ta1 = Tag()
        ta1.position = 1
        ta1.name = 'default'
        ta1.save()

        f = Feed()
        f.title = 'f1'
        f.type = Feed.Type.RSS
        f.external_uid = '12345'
        f.save()

        f.tags.add(ta1)
        f.save()

        a = Article()
        a.content = 'content1'
        a.title = 'title1'
        a.description = 'description1'
        a.feed = f
        a.unread = True
        a.save()

        c = Client()

        response = c.get('/')
        articles = response.context['unreadByFeed']

        self.assertEqual(len(articles), 1)

        c.get('/articles/1/read')

        response = c.get('/')
        articles = response.context['unreadByFeed']

        self.assertEqual(len(articles), 0)

    def test_read_all_feed_articles(self):
        ta1 = Tag()
        ta1.position = 1
        ta1.name = 'default'
        ta1.save()

        f = Feed()
        f.title = 'f1'
        f.type = Feed.Type.RSS
        f.external_uid = '12345'
        f.save()

        f.tags.add(ta1)
        f.save()

        a1 = Article()
        a1.content = 'content1'
        a1.title = 'title1'
        a1.description = 'description1'
        a1.link = 'abc'
        a1.feed = f
        a1.save()

        a2 = Article()
        a2.content = 'content2'
        a2.title = 'title2'
        a2.description = 'description2'
        a2.link = 'def'
        a2.feed = f
        a2.save()

        c = Client()

        c.get('/articles/1/read-all')

        response = c.get('/')
        articles = response.context['unreadByFeed']

        self.assertEqual(len(articles), 0)
