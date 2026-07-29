from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Category, Comment


class ModelTests(TestCase):
    """测试数据模型"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpass')
        self.category = Category.objects.create(name='Python', slug='python')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Python')

    def test_post_str(self):
        post = Post.objects.create(
            title='测试文章', slug='test-post', content='正文内容',
            author=self.user, category=self.category, status='published',
        )
        self.assertEqual(str(post), '测试文章')

    def test_comment_str_truncates(self):
        post = Post.objects.create(
            title='T', slug='t', content='x', author=self.user, category=self.category,
        )
        comment = Comment.objects.create(
            post=post, author=self.user, content='A' * 100,
        )
        self.assertEqual(len(str(comment)), 50)


class PostListTests(TestCase):
    """测试文章列表页"""

    def setUp(self):
        self.user = User.objects.create_user('author', password='pass')
        self.category = Category.objects.create(name='Django', slug='django')
        self.published = Post.objects.create(
            title='公开文章', slug='public', content='公开内容',
            author=self.user, category=self.category, status='published',
        )
        self.draft = Post.objects.create(
            title='草稿文章', slug='draft', content='草稿内容',
            author=self.user, category=self.category, status='draft',
        )

    def test_unauthenticated_sees_only_published(self):
        """未登录用户只看已发布"""
        response = self.client.get(reverse('post_list'))
        self.assertContains(response, '公开文章')
        self.assertNotContains(response, '草稿文章')

    def test_authenticated_sees_all(self):
        """已登录用户看全部"""
        self.client.login(username='author', password='pass')
        response = self.client.get(reverse('post_list'))
        self.assertContains(response, '公开文章')
        self.assertContains(response, '草稿文章')

    def test_search(self):
        """搜索功能"""
        response = self.client.get(reverse('post_list') + '?q=公开')
        self.assertContains(response, '公开文章')
        self.assertNotContains(response, '草稿文章')

    def test_pagination(self):
        """分页：每页最多5篇"""
        for i in range(7):
            Post.objects.create(
                title=f'文章{i}', slug=f'post-{i}', content='x',
                author=self.user, category=self.category, status='published',
            )
        response = self.client.get(reverse('post_list'))
        self.assertEqual(len(response.context['page_obj']), 5)  # 第一页5篇


class PostDetailTests(TestCase):
    """测试文章详情页"""

    def setUp(self):
        self.author = User.objects.create_user('author', password='pass')
        self.other = User.objects.create_user('other', password='pass')
        self.category = Category.objects.create(name='Python', slug='python')
        self.draft = Post.objects.create(
            title='草稿', slug='draft', content='秘密',
            author=self.author, category=self.category, status='draft',
        )
        self.published = Post.objects.create(
            title='已发布', slug='pub', content='公开',
            author=self.author, category=self.category, status='published',
        )

    def test_anyone_can_see_published(self):
        """任何人都能看已发布文章"""
        response = self.client.get(reverse('post_detail', args=['pub']))
        self.assertEqual(response.status_code, 200)

    def test_author_can_see_own_draft(self):
        """作者能看自己的草稿"""
        self.client.login(username='author', password='pass')
        response = self.client.get(reverse('post_detail', args=['draft']))
        self.assertEqual(response.status_code, 200)

    def test_others_cannot_see_draft(self):
        """其他人不能看草稿"""
        self.client.login(username='other', password='pass')
        response = self.client.get(reverse('post_detail', args=['draft']))
        self.assertRedirects(response, reverse('post_list'))


class PostCreateTests(TestCase):
    """测试创建文章"""

    def setUp(self):
        self.user = User.objects.create_user('author', password='pass')
        self.category = Category.objects.create(name='Django', slug='django')

    def test_unauthenticated_redirected(self):
        """未登录不能创建"""
        response = self.client.get(reverse('post_new'))
        self.assertRedirects(response, '/login/?next=/post/new/')

    def test_create_post(self):
        """登录后创建文章"""
        self.client.login(username='author', password='pass')
        response = self.client.post(reverse('post_new'), {
            'title': '新文章', 'slug': 'new-post', 'content': '内容',
            'category': self.category.id, 'status': 'published',
        })
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)


class PostEditDeleteTests(TestCase):
    """测试编辑和删除"""

    def setUp(self):
        self.author = User.objects.create_user('author', password='pass')
        self.other = User.objects.create_user('other', password='pass')
        self.category = Category.objects.create(name='Python', slug='python')
        self.post = Post.objects.create(
            title='原文', slug='original', content='原始内容',
            author=self.author, category=self.category,
        )

    def test_only_author_can_edit(self):
        """只有作者能编辑"""
        self.client.login(username='other', password='pass')
        response = self.client.get(reverse('post_edit', args=['original']))
        self.assertRedirects(response, reverse('post_list'))

    def test_author_can_edit(self):
        """作者编辑自己的文章"""
        self.client.login(username='author', password='pass')
        response = self.client.post(reverse('post_edit', args=['original']), {
            'title': '改后', 'slug': 'original', 'content': '新内容',
            'category': self.category.id, 'status': 'published',
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, '改后')

    def test_only_author_can_delete(self):
        """只有作者能删除"""
        self.client.login(username='other', password='pass')
        response = self.client.post(reverse('post_delete', args=['original']))
        self.assertEqual(Post.objects.count(), 1)  # 没删掉

    def test_author_can_delete(self):
        """作者删除自己的文章"""
        self.client.login(username='author', password='pass')
        response = self.client.post(reverse('post_delete', args=['original']))
        self.assertEqual(Post.objects.count(), 0)


class CategoryPostsTests(TestCase):
    """测试分类筛选"""

    def setUp(self):
        self.user = User.objects.create_user('author', password='pass')
        self.cat = Category.objects.create(name='Python', slug='python')
        Post.objects.create(
            title='公开', slug='pub', content='x',
            author=self.user, category=self.cat, status='published',
        )
        Post.objects.create(
            title='草稿', slug='draft', content='x',
            author=self.user, category=self.cat, status='draft',
        )

    def test_unauthenticated_sees_only_published_in_category(self):
        """未登录在分类页也只看已发布"""
        response = self.client.get(reverse('category_posts', args=['python']))
        self.assertContains(response, '公开')
        self.assertNotContains(response, '草稿')


class RegisterTests(TestCase):
    """测试注册"""

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, reverse('post_list'))


class LikeTests(TestCase):
    """测试点赞"""

    def setUp(self):
        self.user = User.objects.create_user('fan', password='pass')
        self.category = Category.objects.create(name='X', slug='x')
        self.post = Post.objects.create(
            title='好文', slug='good', content='赞',
            author=self.user, category=self.category, status='published',
        )

    def test_like_toggles(self):
        """点赞/取消点赞切换"""
        self.client.login(username='fan', password='pass')
        # 点赞
        self.client.post(reverse('like_post', args=['good']))
        self.assertEqual(self.post.likes.count(), 1)
        # 取消
        self.client.post(reverse('like_post', args=['good']))
        self.assertEqual(self.post.likes.count(), 0)


class CommentTests(TestCase):
    """测试评论"""

    def setUp(self):
        self.user = User.objects.create_user('reader', password='pass')
        self.category = Category.objects.create(name='X', slug='x')
        self.post = Post.objects.create(
            title='文', slug='post', content='内容',
            author=self.user, category=self.category, status='published',
        )

    def test_add_comment(self):
        """登录后添加评论"""
        self.client.login(username='reader', password='pass')
        response = self.client.post(
            reverse('post_comments', args=['post']),
            {'content': '好文章！'},
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertRedirects(response, reverse('post_detail', args=['post']))

    def test_unauthenticated_cannot_comment(self):
        """未登录不能评论"""
        response = self.client.post(
            reverse('post_comments', args=['post']),
            {'content': '垃圾评论'},
        )
        self.assertEqual(Comment.objects.count(), 0)
