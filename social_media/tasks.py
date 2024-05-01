from celery import shared_task
from django.utils import timezone

from social_media.models import PostponedPost


@shared_task
def publish_postponed_posts() -> None:

    post_for_publication = PostponedPost.objects.filter(
        published=False,
        postponed_at__lte=timezone.now(),
    )

    for post in post_for_publication.all():
        post.publish()
