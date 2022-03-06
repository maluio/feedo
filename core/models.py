from django.db import models
from django.utils import timezone


class Tag(models.Model):
    class Meta:
        ordering = ['-position']

    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=100)
    position = models.IntegerField(default=-1)

    unread_article_count = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_position = self.position

    def __str__(self):
        return self.name

    def handle_position(self):
        if self.position == self.initial_position:
            return
        # todo : handle position
        pass

    # override model save method
    def save(self, *args, **kwargs):
        self.handle_position()
        super().save(*args, **kwargs)


class ActiveFeedManager(models.Manager):
    # Q: Make sure that filter applies to all queries
    # Django Modifying a manager’s initial QuerySet
    # https://docs.djangoproject.com/en/dev/topics/db/managers/#modifying-a-manager-s-initial-queryset
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Feed(models.Model):
    class Type(models.TextChoices):
        RSS = 'RSS'
        REDDIT = 'Reddit'
        TWITTER = 'Twitter'
        MAIL = 'Mail'

    DEFAULT_TAG = 'default'

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    title = models.TextField()
    external_uid = models.TextField(unique=True)
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.RSS
    )
    extras = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    tags = models.ManyToManyField(to=Tag)

    # Managers
    objects = models.Manager()  # The default manager.
    objects_active = ActiveFeedManager()

    def __str__(self):
        return self.title

    def unread_count(self):
        return Article.objects.filter(unread=1, feed=self).count()

    def handle_extras_on_save(self):
        if not self.extras:
            if self.type == self.Type.RSS:
                self.extras = {"filtered": []}
            if self.type == self.Type.TWITTER:
                self.extras = {"username": ""}
            else:
                self.extras = {}

    # override model save method
    def save(self, *args, **kwargs):
        self.handle_extras_on_save()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class Article(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, blank=True, null=True)
    description = models.CharField(max_length=10000, blank=True, null=True)
    content = models.CharField(max_length=10000, blank=True, null=True)
    link = models.TextField(unique=True)
    image = models.TextField(blank=True, null=True)
    unread = models.BooleanField(default=True)
    saved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    # override model save method
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def mark_read(self):
        self.unread = False
