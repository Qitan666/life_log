from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    """Blog post"""
    title = models.CharField('Title', max_length=200)
    content = models.TextField('Body')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Author', related_name='posts')
    image = models.ImageField('Cover image', upload_to='blog/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    is_published = models.BooleanField('Published', default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog post'
        verbose_name_plural = 'Blog posts'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    """Comment on a post"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Post', related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Author', related_name='blog_comments')
    content = models.TextField('Content', max_length=1000)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f'Comment by {self.author.username} on \"{self.post.title}\"'
