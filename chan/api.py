import itertools
from chan import utils

DVACH_URL = 'http://2ch.hk'


class Page(object):

    """
    Represents a board's page. It has a list of threads presented on the page.

    By default threads will not be fully loaded
    and will have only 3 posts from the head.
    """

    def __init__(self, board_name, index):
        self._threads = []
        self.board_name = board_name
        self.index = index
        self._url = None
        self._json_url = None

    def _format_url(self, fmt):
        """Return string representation of url."""
        index = 'index' if (self.index == 0) else str(self.index)
        return '{}/{}/{}.{}'.format(
            DVACH_URL, self.board_name, index, fmt)

    def __getitem__(self, index):
        return self.threads[index]

    @property
    def url(self):
        """Property which represents url of board page."""
        if not self._url:
            self._url = self._format_url('html')
        return self._url

    @property
    def json_url(self):
        """Property which represents url of json page."""
        if not self._json_url:
            self._json_url = self._format_url('json')
        return self._json_url

    @property
    def threads(self):
        """Property which represents list of board threads."""
        if not self._threads:
            page_json = utils.load_json(self.json_url)
            self._threads = [Thread(self.board_name, thread)
                             for thread in page_json['threads']]
        return self._threads


class Thread(object):

    """
    Represents a 2ch.hk thread.

    If initialization is done by JSON then thread has only original post.
    Initialization by thread's number gathers all the data.
    """

    def __init__(self, board_name, data=None, num=None):
        self.board_name = board_name
        self.num = None
        self.original_post = None
        self.posts = None
        self._url = None
        self._json_url = None
        self.title = None
        self.posts_count = None
        self.files_count = None

        if num:
            # initialization by thread number
            self.num = str(num)
            data = utils.load_json(self.json_url)
        elif not data:
            # no data, no num
            raise Exception('Invalid set of initial arguments')
        self._parse_json(data)
        self._update_files_ulrs()

    def __repr__(self):
        return 'Thread /{}/#{}'.format(self.board_name, self.num)

    def _parse_json(self, data):
        """Get required fields from JSON and inits fields of the class."""
        self.files_count = int(data.get('files_count'))
        self.posts_count = int(data.get('posts_count'))

        # understanding by unique keys what kind of json we are dealing with
        if data.get('posts'):
            # dealing with thread's data from page.json
            self.num = data.get('thread_num')
            self.posts = [Post(data.get('posts')[0])]
        elif data.get('num'):
            # dealing with thread's data from catalog.json
            self.num = data.get('num')
            self.posts = [Post(data)]
        else:
            # dealing with thread.json
            self.posts = [Post(post_data)
                          for post_data in data.get('threads')[0]['posts']]

        self.original_post = self.posts[0]

    def _format_url(self, fmt):
        """Return string representation of url."""
        return '{}/{}/res/{}.{}'.format(
            DVACH_URL, self.board_name, self.num, fmt)

    @property
    def url(self):
        """Property which represents url of board page."""
        if not self._url:
            self._url = self._format_url('html')
        return self._url

    @property
    def json_url(self):
        """Property which represents url of json page."""
        if not self._json_url:
            self._json_url = self._format_url('json')
        return self._json_url

    def _update_files_ulrs(self):
        """Create absolute links of files."""
        for post in self.posts:
            for attachment in post.attachments:
                attachment.url = '{}/{}/{}'.format(
                    DVACH_URL, self.board_name, attachment.url)

    def update(self):
        """Update thread's content to the latest data."""

        thread_json = utils.load_json(self.json_url)
        self.title = thread_json['title']
        self.files_count = int(thread_json['files_count'])
        self.posts_count = int(thread_json['posts_count'])

        posts_length = len(self.posts) - 1  # OP is omitted
        gap = self.posts_count - posts_length
        if gap:
            missed_posts = thread_json['threads'][0]['posts'][-gap:]
            self.posts += [Post(data) for data in missed_posts]
        self._update_files_ulrs()

    def __getitem__(self, index):
        return self.posts[index]

    @property
    def pictures(self):
        """
        Return list of AttachedFile objects of all pictures in the thread.
        """
        return list(itertools.chain.from_iterable(
            post.pictures for post in self.posts))

    @property
    def webms(self):
        """
        Return list of AttachedFile objects of all wemb files in the thread.
        """
        return list(itertools.chain.from_iterable(
            post.webms for post in self.posts))


class Post(object):

    """
    Represents a single post in the thread.
    """

    def __init__(self, data):
        self.message = data.get('comment')
        self.attachments = [AttachedFile(attachment)
                            for attachment in data.get('files')]
        self._pictures = None
        self._webms = None

    @property
    def pictures(self):
        if not self._pictures:
            self._pictures = [attachment for attachment in self.attachments
                              if attachment.is_picture()]
        return self._pictures

    @property
    def webms(self):
        if not self._webms:
            self._webms = [attachment for attachment in self.attachments
                           if attachment.is_webm()]
        return self._webms


class AttachedFile(object):

    """
    Represents a file related to post.
    """

    def __init__(self, data):
        self.name = data.get('name')
        self.size = int(data.get('size'))
        self.type = data.get('type')
        self.url = data.get('path')

    def __repr__(self):
        return 'File {}'.format(self.name)

    def is_picture(self):
        return self.name.endswith(('.jpg', '.png'))

    def is_webm(self):
        return self.name.endswith('.webm')


def get_preview(board):
    """
    Return a dictionary which represents light version of threads.

    Keys in result dictionary are thread numbers.
    Values are titles of original posts.
    """
    # TODO: check if board is valid
    url = '{}/{}/threads.json'.format(DVACH_URL, board)
    data = utils.load_json(url)
    return {
        thread['num']: thread['subject'] for thread in data.get('threads')
    }


def get_all_threads(board):
    """
    Return a list of Thread objects gathered from board.

    The list consists of all threads from board.
    Each element from this list has only original post.
    """
    # TODO: check if board is valid
    url = '{}/{}/catalog.json'.format(DVACH_URL, board)
    data = utils.load_json(url)
    return [Thread(board, thread_data) for thread_data in data.get('threads')]
