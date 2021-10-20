from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа123',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        """Проверка: правильно ли отображается значение поля __str__"""
        post = PostModelTest.post
        expected = post.text
        self.assertEqual(expected, str(post))

    def test_models_have_correct_group_names(self):
        """Проверка: правильно ли отображается значение поля __str__"""
        group = PostModelTest.group
        excepted = group.title
        self.assertEqual(excepted, str(group))
