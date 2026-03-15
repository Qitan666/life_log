from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, Comment
from .forms import PostForm, CommentForm


def post_list(request):
    qs = Post.objects.filter(is_published=True).annotate(comment_total=Count('comments', distinct=True))

    category = request.GET.get('category', '').strip()
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'new').strip()

    if category:
        qs = qs.filter(category=category)

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(author__username__icontains=q)
        )

    if sort == 'old':
        qs = qs.order_by('created_at')
    elif sort == 'popular':
        if hasattr(Post, 'likes'):
            qs = qs.annotate(like_total=Count('likes')).order_by('-like_total', '-created_at')
        else:
            qs = qs.order_by('-created_at')
    else:
        qs = qs.order_by('-created_at')

    paginator = Paginator(qs, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Post.CATEGORY_CHOICES

    current_category_label = 'All Posts'
    if category:
        category_map = dict(Post.CATEGORY_CHOICES)
        current_category_label = category_map.get(category, 'Filtered Posts')

    liked_post_ids = set()
    if request.user.is_authenticated and hasattr(request.user, 'liked_posts'):
        liked_post_ids = set(request.user.liked_posts.values_list('id', flat=True))

    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'current_category_label': current_category_label,
        'q': q,
        'sort': sort,
        'liked_post_ids': liked_post_ids,
    })


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    comments = post.comments.select_related('author').all()

    comment_form = CommentForm() if request.user.is_authenticated else None

    has_liked = False
    if request.user.is_authenticated:
        has_liked = post.likes.filter(pk=request.user.pk).exists()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'has_liked': has_liked,
    })

@login_required
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk, is_published=True)

    if request.method != 'POST':
        return redirect(post.get_absolute_url())

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, 'Comment posted.')
    else:
        messages.error(request, 'Please fix the comment and try again.')

    return redirect(post.get_absolute_url() + '#comments')


@login_required
def comment_edit(request, pk, comment_id):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    comment = get_object_or_404(Comment, pk=comment_id, post=post, author=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated.')
            return redirect(post.get_absolute_url() + '#comments')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment_form.html', {
        'post': post,
        'comment': comment,
        'form': form,
    })


@login_required
def comment_delete(request, pk, comment_id):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    comment = get_object_or_404(Comment, pk=comment_id, post=post, author=request.user)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted.')
        return redirect(post.get_absolute_url() + '#comments')

    return render(request, 'blog/comment_confirm_delete.html', {
        'post': post,
        'comment': comment,
    })


@login_required
def post_create(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully.')
            return redirect(post.get_absolute_url())
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create post'})


@login_required
def post_edit(request, pk):
    """Edit an existing post"""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated.')
            return redirect(post.get_absolute_url())
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'post': post, 'title': 'Edit post'})


@login_required
def post_delete(request, pk):
    """Delete a post"""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('blog:post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
def toggle_like(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    post = get_object_or_404(Post, pk=pk, is_published=True)

    liked = False
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': post.total_likes(),
    })
