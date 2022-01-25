# posts/tests/tests_form.py
import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, User, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestsCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Test group',
            slug='test',
            description='Группа для тестирования', )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='AdminTest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            group=TestsCreateForm.group,
            text="Текст для тестовой группы",
            author=User.objects.get(username='AdminTest'),
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='Комментарий для теста'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create(self):
        """Проверка создания нового поста,
        авторизированным пользователем"""
        post_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'group': self.group.id,
            'text': 'Текст для группы',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            group=form_data["group"],
            text=form_data['text'],
            image='posts/small.gif').exists())
        added_post = Post.objects.first()
        self.assertEqual(added_post.text, form_data['text'])
        self.assertEqual(added_post.group.id, form_data['group'])
        self.assertEqual(added_post.author.username, self.user.username)

    def test_signup(self):
        """Валидная форма создает третьего юзера."""
        user_count = User.objects.count()
        form_data = {'first_name': 'Admin',
                     'last_name': 'Test',
                     'username': 'AdminTest3',
                     'email': 'AdminTest@yandex.ru',
                     'password1': 'passwordTest123',
                     'password2': 'passwordTest123'}

        # Отправили POST-запрос
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True)

        # Проверили редирект
        self.assertRedirects(response, reverse('users:login'))
        self.assertEqual(User.objects.count(), user_count + 1)

    def test_post_edit(self):
        """Проверка редактирования поста"""
        old_post = Post.objects.latest('created')
        form_data = {'group': old_post.group.id,
                     'text': 'Отредактированный текст поста'}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_post.id}),
            data=form_data)
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': old_post.id}))
        new_post = Post.objects.first()
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author.username, self.user.username)

    def test_add_comment_in_post_detail(self):
        old_comment = Comment.objects.first()
        count_comments = Comment.objects.count()
        form_data = {'post': self.post,
                     'author': self.user,
                     'text': 'Второй комментарий для теста'}

        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': old_comment.id}),
            data=form_data)
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': old_comment.id}))
        self.assertEqual(Comment.objects.count(), count_comments + 1)
        new_comment = Comment.objects.first()
        self.assertEqual(new_comment.text, form_data['text'])
        self.assertEqual(new_comment.author.username,
                         self.user.username)
        self.assertEqual(new_comment.post.pk, self.post.pk)

    def test_post_create_for_guest(self):
        """Проверка создания нового поста,
        неавторизованным пользователем"""
        form_data = {
            'group': self.group.id,
            'text': 'Текст неавторизованного пользователя',
        }
        response = self.guest_client.post(reverse('posts:post_create'),
                                          data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'users:login') + '?next=' + reverse('posts:post_create'))
        self.assertFalse(Post.objects.filter(
            text='Текст неавторизованного пользователя'
        ).exists(), 'Запись не должна добавляться!')
