# posts/tests/test_views.py
from itertools import islice

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, Follow
from yatube.settings import SHOW_MAX_POSTS

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # Создаем второго юзера для теста подписок
        cls.new_user = User.objects.create_user(username='new_user')
        cls.authorized_new_user = Client()
        cls.authorized_new_user.force_login(cls.new_user)

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
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField,
                       'image': forms.ImageField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('is_edit'), True)
        # form_fields уже проверен

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post_count = Post.objects.count()
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('count_posts'), post_count)

    def test_profile_follow(self):
        """Тестирование подписки на автора поста."""
        count_follower = self.new_user.follower.count()
        self.authorized_new_user.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.post.author}))
        count_follower_before = self.new_user.follower.count()
        self.assertEqual(count_follower_before, count_follower + 1)
        last_follow = Follow.objects.first()
        self.assertEqual(last_follow.user_id, self.new_user.id)
        self.assertEqual(last_follow.author_id, self.post.author.id)

    def test_profile_unfollow(self):
        """Тестирование отписки от автора поста."""
        Follow.objects.create(user=self.new_user, author=self.post.author)
        count_all_follows = self.new_user.follower.count()
        self.authorized_new_user.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.post.author}))
        count_follows_before_unfollow = self.new_user.follower.count()
        self.assertEqual(count_follows_before_unfollow, count_all_follows - 1)


class PostsForFollowerTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем первого юзера для теста
        cls.author = User.objects.create_user(username='author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        # Создаем второго юзера для теста
        cls.auth_user = User.objects.create_user(username='auth_user')
        cls.authorized_auth_user = Client()
        cls.authorized_auth_user.force_login(cls.auth_user)
        # Создаем группу для теста
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы')

    def test_show_posts_for_follower(self):
        """Тестирование отображение постов с подпиской"""
        count_posts_follow_index_before = Post.objects.filter(
            author__following__user=self.auth_user).count()
        post = Post.objects.create(text='Создаем тестовый пост',
                                   author=self.author, group=self.group)
        # Подписываемся на автора
        Follow.objects.create(user=self.auth_user, author=post.author)
        count_posts_follow_index_after = Post.objects.filter(
            author__following__user=self.auth_user).count()
        self.assertEqual(count_posts_follow_index_after,
                         count_posts_follow_index_before + 1)

    def test_show_posts_for_unfollower(self):
        """Тестирование отображение постов без подписки"""
        count_posts_follow_index_before = Post.objects.filter(
            author__following__user=self.auth_user).count()
        Post.objects.create(text='Создаем тестовый пост',
                            author=self.author, group=self.group)
        posts_follow_index_after = Post.objects.filter(
            author__following__user=self.auth_user).count()
        self.assertEqual(count_posts_follow_index_before,
                         posts_follow_index_after)


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
        """Тестируем пайджинатор на первой странице 'posts:index'"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context.get('page_obj')), SHOW_MAX_POSTS)

    def test_index_second_page(self):
        """Тестируем пайджинатор на второй странице 'posts:index'"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')),
                         PaginatorViewsTest.count_posts_on_page(page=2))

    def test_group_first_page(self):
        """Тестируем пайджинатор на первой странице 'posts:group'"""
        response = self.client.get(
            reverse('posts:group', kwargs={'slug': self.group.slug}))
        self.assertEqual(
            len(response.context.get('page_obj')), SHOW_MAX_POSTS)

    def test_group_second_page(self):
        """Тестируем пайджинатор на второй странице 'posts:group'"""
        response = self.client.get(reverse('posts:group', kwargs={
            'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')),
                         PaginatorViewsTest.count_posts_on_page(page=2))

    def test_profile_first_page(self):
        """Тестируем пайджинатор на первой странице 'posts:profile'"""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(len(response.context.get('page_obj')), SHOW_MAX_POSTS)

    def test_profile_second_page(self):
        """Тестируем пайджинатор на второй странице 'posts:profile'"""
        response = self.client.get(reverse('posts:profile', kwargs={
            'username': self.user.username}) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')),
                         PaginatorViewsTest.count_posts_on_page(page=2))

    def test_cache_for_index(self):
        """Проверка работы кэша на главной странице"""
        GET_ONLY_FIRST = 8
        before_delete = self.client.get(reverse('posts:index'))
        count_before_delete = before_delete.context.get(
            'page_obj').paginator.object_list.count()
        self.assertEqual(count_before_delete, PaginatorViewsTest.batch_size)
        Post.objects.filter(
            id__gt=GET_ONLY_FIRST).delete()  # Оставляем только 8 постов
        after_delete = self.client.get(reverse('posts:index'))
        count_after_delete = after_delete.context.get(
            'page_obj').paginator.object_list.count()
        self.assertEqual(count_after_delete,
                         GET_ONLY_FIRST)  # Проверяем что кол-во == 8
        self.assertNotEqual(before_delete.content, after_delete.content,
                            "Кэширование страницы не работает")
        cache.clear()
        # после очистки кэша делаем 2 запроса
        # и убеждаемся что они совпадают
        after_clear_cache = self.client.get(reverse('posts:index'))
        self.assertNotEqual(after_clear_cache.content,
                            after_delete.content,
                            "Кэширование страницы не работает")

        after_clear_cache_2 = self.client.get(reverse('posts:index'))
        self.assertEqual(after_clear_cache.content,
                         after_clear_cache_2.content,
                         "Кэширование страницы не работает")
