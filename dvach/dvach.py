import utils

DVACH_URL = 'http://2ch.hk'


class Page(object):
    """
    Represents a board's page. It has a list of threads presented on the page.
    By default threads will not be fully loaded 
    and will have only 3 posts from the head.
    """

    def __init__(self, board_name, index):
        self.threads = []
        self.board_name = board_name
        self.index = index
        self._create_urls()
        self._create_threads()

    def _create_urls(self):
        index = 'index' if (self.index == 0) else str(self.index)
        self.url = '{}/{}/{}.html'.format(
            DVACH_URL, self.board_name, index)
        self.url_json = '{}/{}/{}.json'.format(
            DVACH_URL, self.board_name, index)

    def _create_threads(self):
        page_json = utils.load_json(self.url_json)
        for thread in page_json['threads']:
            self.threads.append(Thread(self.board_name, thread))


class Thread(object):
    """
    Represents a 2ch.hk thread. If initialization is done by JSON then 
    thread may not contain all required fileds (depends on JSON data).
    If initialize by thread's number then ALL the essential stuff will be gathered.
    """

    def __init__(self, board_name, data=None, thread_num=None):
        self.board_name = board_name
        self.num = thread_num
        self.original_post = None
        self.posts = []

        if data and not thread_num:
            self._init_by_json(data)
        elif thread_num and not data:
            self._init_by_num(thread_num)
        else:
            raise Exception('Invalid set of initial arguments')

    def _init_by_json(self, data):
        self._parse_json(data)
        self._create_urls()
        self._update_files_ulrs()

    def _init_by_num(self, thread_num):
        self.num = str(thread_num)
        self._create_urls()
        thread_json = self.update()
        self._parse_json(thread_json)

    def _parse_json(self, data):
        "Gets required fields from JSON and inits fields of the class"
        self.files_count = int(data['files_count'])
        self.posts_count = int(data['posts_count'])
        if not self.num:
            # invoked by _init_by_json
            self.num = data['thread_num']
            for post in data['posts']:
                self.posts.append(Post(post))
            self.original_post = self.posts[0]
        else:
            # invoked by _init_by_num
            self.original_post = Post(data['threads'][0]['posts'][0])

    def _create_urls(self):
        self.url = '{}/{}/res/{}.html'.format(
            DVACH_URL, self.board_name, self.num)
        self.url_json = '{}/{}/res/{}.json'.format(
            DVACH_URL, self.board_name, self.num)

    def update(self):
        "Updates thread's content to the latest data."
        if not utils.ping(self.url_json):
            raise Exception('Can not access %s' % self.url_json)
        thread_json = utils.load_json(self.url_json)
        self.title = thread_json['title']
        for post in thread_json['threads'][0]['posts']:
            self.posts.append(Post(post))
        self._update_files_ulrs()
        return thread_json

    def _update_files_ulrs(self):
        "Creates absolute links of files"
        for post in self.posts:
            for attachment in post.files:
                attachment.url = '{}/{}/{}'.format(
                    DVACH_URL, self.board_name, attachment.url_path)


class Post(object):

    def __init__(self, data):
        self.files = []
        self._parse_json(data)

    def _parse_json(self, data):
        self.message = data['comment']
        for f in data['files']:
            self.files.append(AttachedFile(f))


class AttachedFile(object):

    def __init__(self, data):
        self.url = ''
        self._parse_json(data)

    def is_picture(self):
        return self.name.endswith('.jpg')

    def is_webm(self):
        return self.name.endswith('.webm')

    def _parse_json(self, data):
        self.type = data['type']
        self.name = data['name']
        self.size = int(data['size'])
        self.url_path = data['path']
