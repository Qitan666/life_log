from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Post, Comment


class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="pass12345"
        )

    def test_post_str_returns_title(self):
        post = Post.objects.create(
            title="My first post",
            content="Hello world",
            author=self.user,
            category="life",
            is_published=True,
        )
        self.assertEqual(str(post), "My first post")

    def test_total_likes_returns_correct_count(self):
        post = Post.objects.create(
            title="Like test",
            content="Testing likes",
            author=self.user,
            category="tech",
            is_published=True,
        )
        another_user = User.objects.create_user(
            username="another",
            email="another@example.com",
            password="pass12345"
        )
        post.likes.add(another_user)
        self.assertEqual(post.total_likes(), 1)


class PostListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="pass12345"
        )
        self.post = Post.objects.create(
            title="Visible post",
            content="Visible content",
            author=self.user,
            category="life",
            is_published=True,
        )
        self.hidden_post = Post.objects.create(
            title="Hidden post",
            content="Hidden content",
            author=self.user,
            category="tech",
            is_published=False,
        )

    def test_post_list_returns_200(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_list.html")

    def test_post_list_shows_only_published_posts(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertContains(response, "Visible post")
        self.assertNotContains(response, "Hidden post")

    def test_post_list_can_filter_by_category(self):
        response = self.client.get(reverse("blog:post_list"), {"category": "life"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visible post")

    def test_post_list_can_search(self):
        response = self.client.get(reverse("blog:post_list"), {"q": "Visible"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visible post")


class PostCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="writer",
            email="writer@example.com",
            password="pass12345"
        )

    def test_create_post_requires_login(self):
        response = self.client.get(reverse("blog:post_create"))
        login_url = reverse("accounts:login")
        create_url = reverse("blog:post_create")
        self.assertRedirects(response, f"{login_url}?next={create_url}")

    def test_logged_in_user_can_create_post(self):
        self.client.login(username="writer", password="pass12345")

        response = self.client.post(reverse("blog:post_create"), {
            "title": "Created post",
            "category": "travel",
            "content": "Travel content",
            "is_published": True,
        })

        post = Post.objects.get(title="Created post")
        self.assertRedirects(response, reverse("blog:post_detail", args=[post.pk]))
        self.assertEqual(post.author, self.user)


class CommentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="commenter",
            email="commenter@example.com",
            password="pass12345"
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass12345"
        )
        self.post = Post.objects.create(
            title="Comment target",
            content="Post body",
            author=self.other_user,
            category="study",
            is_published=True,
        )

    def test_comment_create_requires_login(self):
        response = self.client.post(
            reverse("blog:comment_create", args=[self.post.pk]),
            {"content": "Nice post"}
        )
        login_url = reverse("accounts:login")
        comment_url = reverse("blog:comment_create", args=[self.post.pk])
        self.assertRedirects(response, f"{login_url}?next={comment_url}")

    def test_logged_in_user_can_create_comment(self):
        self.client.login(username="commenter", password="pass12345")

        response = self.client.post(
            reverse("blog:comment_create", args=[self.post.pk]),
            {"content": "Nice post"}
        )

        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertRedirects(
            response,
            reverse("blog:post_detail", args=[self.post.pk]) + "#comments"
        )


class ToggleLikeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="liker",
            email="liker@example.com",
            password="pass12345"
        )
        self.post = Post.objects.create(
            title="Likeable post",
            content="Post body",
            author=self.user,
            category="mood",
            is_published=True,
        )

    def test_toggle_like_requires_login(self):
        response = self.client.post(reverse("blog:toggle_like", args=[self.post.pk]))
        login_url = reverse("accounts:login")
        like_url = reverse("blog:toggle_like", args=[self.post.pk])
        self.assertRedirects(response, f"{login_url}?next={like_url}")

    def test_toggle_like_adds_like(self):
        self.client.login(username="liker", password="pass12345")
        response = self.client.post(reverse("blog:toggle_like", args=[self.post.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"liked": True, "like_count": 1}
        )

    def test_toggle_like_removes_like(self):
        self.client.login(username="liker", password="pass12345")
        self.post.likes.add(self.user)

        response = self.client.post(reverse("blog:toggle_like", args=[self.post.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"liked": False, "like_count": 0}
        )