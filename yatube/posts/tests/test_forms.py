import shutil
import tempfile

from django.contrib.auth import get_user_model
from ..models import Post, Group, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            id=112
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'author': self.author,
            'text': 'newtext',
            'group': self.group.id,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.post.author}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='newtext',
            group=self.group.id,
            author=self.author
        ).exists())
        self.assertEqual(response.status_code, (HTTPStatus.FOUND))

    def test_post_id(self):
        post_count = Post.objects.count()
        form_data = {
            'author': self.author,
            'text': 'newtext',
            'group': self.group.id,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username':
                                                       self.post.author}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='newtext',
            group=self.group.id,
            author=self.author
        ).exists())
        self.assertEqual(response.status_code, (HTTPStatus.FOUND))

    def test_edit_post(self):
        """Test post save after edit"""
        form_data = {
            'author': self.author,
            'text': 'newtextedit',
            'group': self.group.id,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id':
                                                       self.post.id}))
        self.assertTrue(Post.objects.filter(
            text='newtextedit',
            group=self.group.id,
            author=self.author
        ).exists())
        self.assertEqual(response.status_code, (HTTPStatus.FOUND))

    def test_post_image(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_count = Post.objects.count()
        form_data = {
            'author': self.author,
            'text': 'newtextimage',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username':
                                                       self.post.author}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='newtextimage',
            group=self.group.id,
            author=self.author,
            image='posts/small.gif'
        ).exists())
        self.assertEqual(response.status_code, (HTTPStatus.OK))

    def test_try_comment(self):
        comment_form = {'text': 'текст комментария', }
        response_guest = self.guest_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form)
        response_user = self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form)
        self.assertEqual(response_guest.status_code, (HTTPStatus.FOUND))
        self.assertEqual(response_user.status_code, (HTTPStatus.FOUND))
        self.assertRedirects(response_guest,
                             '/auth/login/?next=/posts/112/comment/')
        self.assertRedirects(response_user, '/posts/112/')

    def test_new_comment(self):
        comment_count = Comment.objects.count()
        comment_form = {'text': 'Комментарий новый', }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': 112}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
