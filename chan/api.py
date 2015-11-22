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

    def _parse_json(self, data):
        """Get required fields from JSON and inits fields of the class."""
        self.files_count = int(data['files_count'])
        self.posts_count = int(data['posts_count'])

        if not self.num:
            self.num = data['thread_num']
        if data.get('posts'):
            # data is json of a page
            self.posts = [Post(data['posts'][0])]
        else:
            # data is json of the thread
            self.posts = [Post(post_data)
                          for post_data in data['threads'][0]['posts']]

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
            for attachment in post.files:
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

    @property
    def pictures(self):
        """
        Property which represents list of AttachedFile objects of
        all pictures in thread.
        """
        return [attachment for post in self.posts for
                attachment in post.files if attachment.is_picture()]

    @property
    def webms(self):
        """
        Property which represents list of AttachedFile objects of
        all wemb files in the thread.
        """
        return [attachment for post in self.posts for
                attachment in post.files if attachment.is_webm()]


class Post(object):

    def __init__(self, data):
        self.message = data.get('comment')
        self.files = [AttachedFile(attachment) for attachment in data['files']]


class AttachedFile(object):

    def __init__(self, data):
        self.name = data.get('name')
        self.size = int(data.get('size'))
        self.type = data.get('type')
        self.url = data.get('path')

    def is_picture(self):
        return self.name.endswith(('.jpg', '.png'))

    def is_webm(self):
        return self.name.endswith('.webm')


def get_preview(board):
    """
    Return a dictionary which represents light version of thread.

    Keys in result dictionary are thread numbers.
    Values are titles of original posts.
    """
    # TODO: check if board is valid
    url = '{}/{}/threads.json'.format(DVACH_URL, board)
    data = utils.load_json(url)
    return {
        thread['num']: thread['subject'] for thread in data['threads']
    }
