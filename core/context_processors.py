from core.models import Article


def unread_count_processor(request):
    count = Article.objects.filter(unread=1).count()
    return {'unread_count': count}
