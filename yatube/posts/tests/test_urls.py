from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_urls_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        static_urls = {
            '/': HTTPStatus.OK,
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK
        }
        for address, response_on_url in static_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertAlmostEqual(response.status_code, response_on_url)

    def test_static_pages_have_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        static_templates = {
            '/': 'posts/index.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in static_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-decsr',
        )
        cls.user = User.objects.create_user(username='Test_user')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            pk='1234',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client(self.user)
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Проверка страниц на доступность."""
        static_urls = {
            '/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/Test_user/': HTTPStatus.OK,
            '/posts/1234/': HTTPStatus.OK,
            '/posts/1234/edit/': HTTPStatus.OK,
        }
        for address, response_on_url in static_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, response_on_url)

    def test_unexisting_page(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_or_update.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Test_user/': 'posts/profile.html',
            '/posts/1234/': 'posts/post_detail.html',
            '/posts/1234/edit/': 'posts/create_or_update.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
