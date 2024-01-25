from celery import shared_task
from celery.utils.log import get_task_logger

from posts.models import Post

logger = get_task_logger(__name__)


@shared_task
def post_schedule_create(post_id, *args, **kwargs):
    post = Post.objects.get(pk=post_id)
    post.is_visible = True
    post.save()

    logger.info(f"Post set to visible successfully. Post ID: {post_id}")
