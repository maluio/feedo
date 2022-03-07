from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models

# Register your models here.
from .models import Feed, Tag, Article


class FeedAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    list_display = ("title", "type", "get_tags", "active", "created_at", "updated_at")
    fields = ("title", "active", "external_uid", "type", "tags", "extras")
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "20"})},
        models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 40})},
    }

    def get_tags(self, obj):
        return ", ".join([t.name for t in obj.tags.all()])


class TagAdmin(admin.ModelAdmin):
    fields = ("name", "position")
    list_display = ("name", "created_at", "position")


def mark_articles_unread(modeladmin, request, queryset):
    queryset.update(unread=True)


class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    fields = ("title", "unread", "saved")
    list_display = ("id", "feed", "created_at", "updated_at", "unread", "saved")
    actions = [mark_articles_unread]


admin.site.register(Feed, FeedAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Article, ArticleAdmin)
