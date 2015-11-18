import unittest
import sys
import json

sys.path.append('../dvach')

from dvach import Thread
from dvach import Post
from dvach import AttachedFile
from dvach import Page


class TestThreadCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('data/thread.json', 'r') as j:
            data = json.loads(j.read())
        cls.board = 'b'
        cls.thread = Thread(data, cls.board)
        cls.url = 'http://2ch.hk/b/res/107239337.html'
        cls.url_json = 'http://2ch.hk/b/res/107239337.json'
        cls.id = '107239337'

    def test_urls_creating(self):
        self.assertEqual(self.thread.url, self.url)
        self.assertEqual(self.thread.url_json, self.url_json)

    def test_json_parsing(self):
        self.assertEqual(self.thread.board_name, self.board)
        self.assertGreater(self.thread.posts_count, 0)
        self.assertGreater(self.thread.files_count, 0)
        self.assertEqual(self.thread.id, self.id)
        self.assertIsNotNone(self.thread.original_post.message)
        self.assertIsInstance(self.thread.original_post, Post)
        self.assertGreater(len(self.thread.original_post.files), 0)


class TestPage(unittest.TestCase):

    def test_index_url_resolving(self):
        page = Page('b', 0)
        self.assertEqual(page.url, 'http://2ch.hk/b/index.html')
        self.assertEqual(page.url_json, 'http://2ch.hk/b/index.json')

    def test_url_resolving(self):
        page = Page('b', 1)
        self.assertEqual(page.url, 'http://2ch.hk/b/1.html')
        self.assertEqual(page.url_json, 'http://2ch.hk/b/1.json')

    def test_threads_creation(self):
        page = Page('b', 2)
        self.assertGreater(len(page.threads), 0)
        self.assertIsInstance(page.threads[0], Thread)
        self.assertNotEqual(page.threads[0].id, page.threads[1].id)


class TestAttachedFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('data/jpg.json', 'r') as j:
            data = json.loads(j.read())
        cls.file = AttachedFile(data)
        cls.name = '14477975927530.jpg'

    def test_json_parsing(self):
        self.assertEqual(self.file.name, self.name)
        self.assertGreater(self.file.size, 0)

    def test_is_picture(self):
        self.assertTrue(self.file.is_picture())
        self.assertFalse(self.file.is_webm())


class TestPost(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('data/post.json', 'r') as j:
            data_post = json.loads(j.read())
        with open('data/post_no_files.json', 'r') as j:
            data_post_no_files = json.loads(j.read())
        cls.post = Post(data_post)
        cls.post_no_files = Post(data_post_no_files)

    def test_json_parsing(self):
        self.assertGreater(len(self.post_no_files.message), 10)
        self.assertGreater(len(self.post.files), 0)
        self.assertIsInstance(self.post.files[0], AttachedFile)
        self.assertEqual(len(self.post_no_files.files), 0)


if __name__ == '__main__':
    unittest.main()
