from django import forms
from .models import Post, Comment


class CommentForm(forms.ModelForm):
    """Comment form (only for logged-in users)"""
    class Meta:
        model = Comment
        fields = ('content',)
        labels = {'content': 'Write your comment'}
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Say something…'}),
        }


class PostForm(forms.ModelForm):
    """Post create/edit form"""
    class Meta:
        model = Post
        fields = ('title', 'content', 'image', 'is_published')
        labels = {
            'title': 'Title',
            'content': 'Body',
            'image': 'Cover image (optional)',
            'is_published': 'Public',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 12}),
        }
