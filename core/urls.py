from django.urls import path

from . import views
from .views import ArticlesSaved

app_name = "core"
urlpatterns = [
    path("", views.index, name="index"),
    path("feeds/<int:feed_id>/articles/", views.feed_articles, name="feed_articles"),
    path(
        "feeds/forward-to-next-feed",
        views.forward_to_next_feed,
        name="forward_to_next_feed",
    ),
    path(
        "feeds/<int:feed_id>/read-all",
        views.article_read_all,
        name="article_read_all",
    ),
    path("articles/saved", ArticlesSaved.as_view(), name="article_saved"),
    path("articles/<int:article_id>/read", views.article_read, name="article_read"),
    path("articles/<int:article_id>/save", views.article_save, name="article_save"),
    path("articles/<int:article_id>", views.article_detail, name="article_detail"),
]
