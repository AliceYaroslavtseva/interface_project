import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from ..models import Post, Group, Follow
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache


User = get_user_model()
TEST_POSTS_COUNT: int = 13
LIMIT: int = 10
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        new_post = Post(author=cls.user,
                        text='Тестовый пост',
                        group=cls.group)
        cls.post = Post.objects.bulk_create([new_post] * TEST_POSTS_COUNT)
        cls.follower = User.objects.create_user(username='follower')

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
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'author'}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={'post_id': '1'}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_author = self.author.username
        post_group = first_object.group.title
        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, 'author')
        self.assertEqual(post_group, 'Тестовый заголовок')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug': 'test-slug'}))
        first_object_group = response.context['page_obj'][0]
        post_author_0 = first_object_group.author.username
        post_text_0 = first_object_group.text
        self.assertEqual(post_author_0, self.user.username)
        self.assertEqual(post_text_0, 'Тестовый пост')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом. """
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username': 'author'}))
        for i in range(len(response.context['page_obj'])):
            post = response.context['page_obj'][i]
            self.assertEqual(post.author, self.user)
        self.assertEqual(response.context.get('author'), self.author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id': 1}))
        post = response.context['post']
        post_text = post.text
        post_author = post.author.username
        post_group = post.group.title
        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, 'user')
        self.assertEqual(post_group, 'Тестовый заголовок')

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_paginator(self):
        pages_to_test = (
            ((reverse('posts:profile', kwargs={'username': 'user'})), LIMIT),
            ((reverse('posts:profile',
             kwargs={'username': 'user'}) + '?page=2'),
             (TEST_POSTS_COUNT - LIMIT)),
            ((reverse('posts:group_list', kwargs={'slug': 'test-slug'})), 10),
            ((reverse('posts:group_list',
             kwargs={'slug': 'test-slug'}) + '?page=2'), 3),
            ((reverse('posts:index')), 10),
            ((reverse('posts:index') + '?page=2'), 3),
        )
        for template, posts_at_page in pages_to_test:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                self.assertEqual(len(response.context['page_obj']),
                                 posts_at_page)

    def test_new_post(self):
        self.post = Post.objects.create(
            author=self.user,
            text='Новый пост',
            group=Group.objects.get(title='Тестовый заголовок')
        )
        new_post_on_page = ((reverse('posts:index')),
                            (reverse('posts:group_list',
                                     kwargs={'slug': 'test-slug'})),
                            (reverse('posts:profile',
                                     kwargs={'username': 'user'})),)
        for page in new_post_on_page:
            with self.subTest(template=page):
                response = self.authorized_client.get(page)
                first_post = response.context['page_obj'][0]
                self.assertEqual(first_post,
                                 Post.objects.get(text='Новый пост'))

    def test_new_post_in_wrong_group(self):
        Group.objects.create(
            title='new_group',
            slug='test-slug-new_group',
            description='Описание',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-new_group'})
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_new_post_image(self):
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
        self.post = Post.objects.create(
            author=self.user,
            text='Новый пост с картинкой',
            group=Group.objects.get(title='Тестовый заголовок'),
            image=uploaded,
        )
        new_post_image_on_page = ((reverse('posts:index')),
                            (reverse('posts:group_list',
                                     kwargs={'slug': 'test-slug'})),
                            (reverse('posts:profile',
                                     kwargs={'username': 'user'})),
                            (reverse('posts:post_detail',
                                     kwargs={'post_id': 1})),)
        for page in new_post_image_on_page:
            with self.subTest(template=page):
                response = self.authorized_client.get(page)
                first_post_image = response.context
                self.assertTrue(first_post_image, Post.objects.filter(text='Новый пост с картинкой',
                                                    group=self.group.id,
                                                    author=self.user,
                                                    image='posts/small.gif'
                                                    ).exists())

    def test_cache_index_page(self):
        self.post = Post.objects.create(
            text='text',
            author=self.user,
            group=self.group,
            )
        self.post.delete()
        content_before = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertIn(self.post.text, str(content_before))
        cache.clear()
        content_cache_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(self.post.text, str(content_cache_clear))

    def test_follow(self):
        follow = Follow.objects.create(author=self.user, user=self.follower)
        follow. save()
        self.assertTrue(Follow.objects. filter(author=self.user,
        user=self.follower).exists())
        self.authorized_follower.post(reverse('posts:profile_unfollow',
        kwargs={'username':'user'}))
        self.assertFalse(Follow.objects.filter(author=self.user,
        user=self.follower).exists())

    def test_new_post(self):
        follow = Follow.objects.create(user=self.user, author=self.author)
        self.post = Post.objects.create(
            author=self.author,
            text='testtext',
            group=self.group
        )
        response_follow = self.authorized_client.get(reverse('posts:follow_index'))
        object = response_follow.context['page_obj']
        self.assertIn(self.post, object, follow)

    def test_not_new_post(self):
        self.post = Post.objects.create(
            author=self.author,
            text='testtext',
            group=self.group
        )
        response_follow = self.authorized_client.get(reverse('posts:follow_index'))
        follow_index = response_follow.context['page_obj']
        posts = Post.objects.filter(author__following__user = self.user)
        self.assertNotIn(follow_index, posts)
