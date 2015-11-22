import json
import sys
import unittest

from chan import utils
from chan.api import AttachedFile, Page, Post, Thread
from chan.api import get_preview, get_all_threads


class TestThreadCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('tests/data/thread.json', 'r') as j:
            data = json.loads(j.read())
        cls.board = 'b'
        cls.thread = Thread(cls.board, data)
        cls.url = 'http://2ch.hk/b/res/107239337.html'
        cls.json_url = 'http://2ch.hk/b/res/107239337.json'
        cls.num = '107239337'

    def test_urls_creating(self):
        self.assertEqual(self.thread.url, self.url)
        self.assertEqual(self.thread.json_url, self.json_url)

    def test_json_parsing(self):
        self.assertEqual(self.thread.board_name, self.board)
        self.assertGreater(self.thread.posts_count, 0)
        self.assertGreater(self.thread.files_count, 0)
        self.assertEqual(self.thread.num, self.num)
        self.assertIsNotNone(self.thread.original_post.message)
        self.assertIsInstance(self.thread.original_post, Post)
        self.assertGreater(len(self.thread.original_post.files), 0)


class TestsWithRealData(unittest.TestCase):

    def setUp(self):
        self.board_name = 'b'
        self.page = Page(self.board_name, 0)
        self.first_thread = self.page.threads[0]

    def test_create_by_num(self):
        thread_num = self.first_thread.num
        new_thread = Thread(self.board_name, num=thread_num)
        self.assertEqual(thread_num, new_thread.num)
        self.assertEqual(new_thread.original_post.message,
                         self.first_thread.original_post.message)
        self.assertEqual(len(new_thread.posts) - 1, new_thread.posts_count)

    def test_file_is_accessible(self):
        pictures = self.first_thread.pictures
        self.assertTrue(utils.ping(pictures[0].url))
        thread = Thread(self.board_name, num=self.first_thread.num)
        pictures = self.first_thread.pictures
        self.assertTrue(utils.ping(pictures[0].url))

    def test_update_thread(self):
        n = len(self.first_thread.posts)
        self.first_thread.update()
        self.assertGreater(len(self.first_thread.posts), n)
        self.assertGreater(len(self.first_thread.title), 0)
        n = len(self.first_thread.posts)
        self.assertEqual(self.first_thread.posts_count, n - 1)

    def test_update_not_duplicates(self):
        self.first_thread.update()
        len_before = len(self.first_thread.posts)
        self.first_thread.update()
        len_after = len(self.first_thread.posts)
        self.assertLess(len_after - len_before, 5)
        self.assertEqual(len(self.first_thread.posts) - 1,
                         self.first_thread.posts_count)

    def test_get_pictures(self):
        pictures = self.first_thread.pictures
        if self.first_thread.files_count > 10:
            self.assertGreater(len(pictures), 0)
        for pic in pictures:
            self.assertTrue(pic.is_picture())
        urls = [pic.url for pic in pictures]
        self.assertEqual(len(set(urls)), len(urls))


class TestPage(unittest.TestCase):

    def test_index_url_resolving(self):
        page = Page('b', 0)
        self.assertEqual(page.url, 'http://2ch.hk/b/index.html')
        self.assertEqual(page.json_url, 'http://2ch.hk/b/index.json')

    def test_url_resolving(self):
        page = Page('b', 1)
        self.assertEqual(page.url, 'http://2ch.hk/b/1.html')
        self.assertEqual(page.json_url, 'http://2ch.hk/b/1.json')

    def test_threads_creation(self):
        page = Page('b', 2)
        self.assertGreater(len(page.threads), 0)
        self.assertIsInstance(page.threads[0], Thread)
        self.assertNotEqual(page.threads[0].num, page.threads[1].num)


class TestAttachedFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('tests/data/jpg.json', 'r') as j:
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
        with open('tests/data/post.json', 'r') as j:
            data_post = json.loads(j.read())
        with open('tests/data/post_no_files.json', 'r') as j:
            data_post_no_files = json.loads(j.read())
        cls.post = Post(data_post)
        cls.post_no_files = Post(data_post_no_files)

    def test_json_parsing(self):
        self.assertGreater(len(self.post_no_files.message), 10)
        self.assertGreater(len(self.post.files), 0)
        self.assertIsInstance(self.post.files[0], AttachedFile)
        self.assertEqual(len(self.post_no_files.files), 0)

class TestModuleFunctions(unittest.TestCase):

    def test_get_preview(self):
        board = get_preview('wrk')
        self.assertGreater(len(board.keys()), 0)
        thread = Thread('wrk', num=board.keys()[0])
        self.assertEqual(thread.num, board.keys()[0])

    def test_get_all_threads(self):
        board = get_all_threads('wrk')
        self.assertGreater(len(board), 0)
        thread = Thread('wrk', num=board[0].num)
        self.assertEqual(thread.num, board[0].num)
        self.assertIsNotNone(board[0].original_post.files)


if __name__ == '__main__':
    unittest.main()
