from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('life', 'Life'),
        ('study', 'Study'),
        ('travel', 'Travel'),
        ('food', 'Food'),
        ('mood', 'Mood'),
        ('tech', 'Tech'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='life')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.pk])

    def total_likes(self):
        return self.likes.count() if hasattr(self, 'likes') else 0


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'