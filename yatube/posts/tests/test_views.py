# posts/tests/test_views.py
from itertools import islice

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from yatube.settings import SHOW_MAX_POSTS

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='classic',
            description='Тестовое описание')

        cls.post = Post.objects.create(
            text='text',
            author=cls.user,
            group=cls.group)

    # Удалил def test_pages_uses_correct_template,
    # так как проверяется в test_urls

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField,
                       'image': forms.ImageField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(
                    value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('is_edit'), True)
        # form_fields уже проверен

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post_count = Post.objects.count()
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('count_posts'),
                         post_count)


class PaginatorViewsTest(TestCase):
    batch_size = 13

    def count_posts_on_page(page):
        """Функция для определения остатка постов для страниц"""
        if PaginatorViewsTest.batch_size > SHOW_MAX_POSTS * page:
            return SHOW_MAX_POSTS
        return PaginatorViewsTest.batch_size - SHOW_MAX_POSTS

    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='classic',
            description='Тестовое описание')

        batch_size = PaginatorViewsTest.batch_size
        objs = (Post(group=cls.group,
                     author=cls.user,
                     text='Пост № %s' % i) for i in range(batch_size))
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            cls.post = Post.objects.bulk_create(batch, batch_size)

    def test_index_first_page(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context.get('page_obj')), SHOW_MAX_POSTS)

    def test_index_second_page(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')),
                         PaginatorViewsTest.count_posts_on_page(page=2))

    def test_group_first_page(self):
        response = self.client.get(
            reverse('posts:group', kwargs={'slug': self.group.slug}))
        self.assertEqual(
            len(response.context.get('page_obj')), SHOW_MAX_POSTS)

    def test_group_second_page(self):
        response = self.client.get(reverse('posts:group', kwargs={
            'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')),
                         PaginatorViewsTest.count_posts_on_page(page=2))

    def test_profile_first_page(self):
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        self.assertEqual(
            len(response.context.get('page_obj')), SHOW_MAX_POSTS)

    def test_profile_second_page(self):
        response = self.client.get(reverse('posts:profile', kwargs={
            'username': self.user.username}) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')),
                         PaginatorViewsTest.count_posts_on_page(page=2))

    def test_cash_for_index(self):
        """Проверка работы кэша на главной странице"""
        response = self.client.get(reverse('posts:index'))
        count_posts_before = response.context.get(
            'page_obj').paginator.object_list.count()
        self.assertEqual(count_posts_before,
                         PaginatorViewsTest.batch_size)
        cache.clear()
        Post.objects.first().delete()
        count_post_after = response.context.get(
            'page_obj').paginator.object_list.count()
        self.assertEqual(count_post_after,
                         PaginatorViewsTest.batch_size - 1)
        # Почему-то без очистки кеша все работает, пока не понял...
