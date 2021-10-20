from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-decsr',
        )
        cls.user = User.objects.create_user(username='Test_user')
        cls.post_list = []
        for i in range(13):
            cls.post_list.append(Post(
                text=f'Текст № {i}',
                author=cls.user,
                group=cls.group,
                id=i
            ))
        cls.Test_post = Post.objects.bulk_create(cls.post_list, 13)
        cls.index_url = reverse(
            'posts:index'
        )
        cls.group_list_url = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug}
        )
        cls.templates_pages_names = {
            reverse(
                'posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': cls.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.user}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': '0'}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': '0'}): 'posts/create_or_update.html',
            reverse(
                'posts:post_create'): 'posts/create_or_update.html'
        }
        cls.reverse_page_names_post = {
            reverse('posts:index'): cls.group.slug,
            reverse('posts:group_list', kwargs={
                'slug': cls.group.slug}): cls.group.slug,
            reverse('posts:profile', kwargs={
                'username': cls.user}): cls.group.slug
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client(self.user)
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.index_url)
        object = response.context['page_obj'][0]
        post_id = object.id
        post_text = object.text
        post_author = object.author
        post_group = object.group
        self.assertEqual(post_text, self.Test_post[post_id].text)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, self.group)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.group_list_url)
        object = response.context['page_obj'][0]
        post_title = object.group.title
        post_slug = object.group.slug
        post_description = object.group.description
        self.assertEqual(post_title, self.group.title)
        self.assertEqual(post_slug, self.group.slug)
        self.assertEqual(post_description, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        for object in response.context['page_obj']:
            post_id = object.id
            post_text = object.text
            post_author = object.author
            post_group = object.group
            self.assertEqual(post_text, self.Test_post[post_id].text)
            self.assertEqual(post_author, self.user)
            self.assertEqual(post_group, self.group)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.Test_post[0].id}
                    )
        )
        self.assertEqual(response.context['post'].text, self.Test_post[0].text)
        self.assertEqual(response.context['post'].author, self.user)
        self.assertEqual(response.context['post'].group, self.group)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        post_example = self.Test_post[0]
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_example.id})
        )
        self.assertEqual(response.context['post'].text, post_example.text)
        self.assertEqual(response.context['post'].group, self.group)

    def test_pages_with_paginator(self):
        """Тестирование страниц с паджинатором."""
        pages_with_paginator = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user})
        ]
        # Подсчет кол-ва страниц
        num = (len(self.Test_post) // 10) + 1
        for page in pages_with_paginator:
            # Если одна страница в паджинаторе, то подсчитываем кол-во постов
            if num == 1:
                response = self.authorized_client.get(
                    page + '?page=' + str(num)
                )
                self.assertEqual(
                    len(response.context['page_obj']),
                    len(self.Test_post)
                )
            # Если несколько страниц, то проверяем количество на первой и
            # последних страницах
            else:
                response_first = self.authorized_client.get(
                    page + '?page=' + '1'
                )
                response_last = self.authorized_client.get(
                    page + '?page=' + str(num)
                )
                self.assertEqual(
                    len(response_first.context['page_obj']),
                    10
                )
                self.assertEqual(
                    len(response_last.context['page_obj']),
                    (len(self.Test_post) % 10)
                )

    def test_post_in_index_group_profile_create(self):
        """Проверка:созданный пост появился на главной, в группе, в профиле."""
        for value, expected in self.reverse_page_names_post.items():
            response = self.authorized_client.get(value)
            for object in response.context['page_obj']:
                post_group = object.group.slug
                with self.subTest(value=value):
                    self.assertEqual(post_group, expected)

    def test_post_not_in_foreign_group(self):
        """Проверка: созданный пост не появился в чужой группе"""
        Test_group = Group.objects.create(
            title='test-title 2',
            slug='test-slug_2',
            description='test-decsr 2',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': Test_group.slug})
        )
        for object in response.context['page_obj']:
            post_slug = object.group.slug
            self.assertNotEqual(post_slug, self.group.slug)
