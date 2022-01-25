from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Фикстуры для тестов"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='classic',
            description='Тестовое описание',
        )

        Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        """Создание неавторизованного и авторизованного клиента"""
        self.guest_client = Client()  # Создаем неавторизованный клиент
        self.authorized_client = Client()  # Создаем пользователя
        self.authorized_client.force_login(
            self.user)  # Авторизуем пользователя

    def test_url_index_and_status(self):
        """URL-адрес использует соответствующий шаблон и статус HTTP."""
        template = 'posts:index'
        response = self.authorized_client.get(reverse(template))
        self.assertTemplateUsed(response, 'posts/index.html')
        auth_status = response.status_code
        self.assertEqual(auth_status, HTTPStatus.OK)
        guest_status = self.guest_client.get(
            reverse(template)).status_code
        self.assertEqual(guest_status, HTTPStatus.OK)

    def test_url_post_create_and_status(self):
        """URL-адрес использует соответствующий шаблон и статус HTTP."""
        template = 'posts:post_create'
        response = self.authorized_client.get(reverse(template))
        self.assertTemplateUsed(response, 'posts/create_post.html')
        auth_status = response.status_code
        self.assertEqual(auth_status, HTTPStatus.OK)
        guest_status = self.guest_client.get(
            reverse(template)).status_code
        self.assertEqual(guest_status, HTTPStatus.FOUND)

    def test_url_group_and_status(self):
        """URL-адрес использует соответствующий шаблон и статус HTTP."""
        template = reverse('posts:group',
                           kwargs={'slug': self.group.slug})
        response = self.authorized_client.get(template)
        self.assertTemplateUsed(response, 'posts/group_list.html')
        auth_status = response.status_code
        self.assertEqual(auth_status, HTTPStatus.OK)
        guest_status = self.guest_client.get(template).status_code
        self.assertEqual(guest_status, HTTPStatus.OK)

    def test_url_profile_and_status(self):
        """URL-адрес использует соответствующий шаблон и статус HTTP."""
        template = reverse('posts:profile',
                           kwargs={'username': self.user.username})
        response = self.authorized_client.get(template)
        self.assertTemplateUsed(response, 'posts/profile.html')
        auth_status = response.status_code
        self.assertEqual(auth_status, HTTPStatus.OK)
        guest_status = self.guest_client.get(template).status_code
        self.assertEqual(guest_status, HTTPStatus.OK)

    def test_url_post_detail_and_status(self):
        """URL-адрес использует соответствующий шаблон и статус HTTP."""
        template = reverse('posts:post_detail',
                           kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(template)
        self.assertTemplateUsed(response, 'posts/post_detail.html')
        auth_status = response.status_code
        self.assertEqual(auth_status, HTTPStatus.OK)
        guest_status = self.guest_client.get(template).status_code
        self.assertEqual(guest_status, HTTPStatus.OK)
