import utils

DVACH_URL = 'http://2ch.hk'


class Page(object):

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
            self.threads.append(Thread(thread, self.board_name))

class Thread(object):

    def __init__(self, data, board_name):
        self.board_name = board_name
        self.posts = []
        self._parse_json(data)
        self._create_urls()

    def _parse_json(self, data):
        self.files_count = int(data['files_count'])
        self.posts_count = int(data['posts_count'])
        self.id = data['thread_num']
        self.original_post = Post(data['posts'][0])

    def _create_urls(self):
        self.url = '{}/{}/res/{}.html'.format(
            DVACH_URL, self.board_name, self.id)
        self.url_json = '{}/{}/res/{}.json'.format(
            DVACH_URL, self.board_name, self.id)

    def update(self):
        thread_json = utils.load_json(self.url_json)
        self.title = thread_json['threads'][0]['title']
        for post in thread_json['threads'][0]['posts']:
            self.posts.append(Post(post))
        # create absolute links of files
        for post in self.posts:
            for attachment in post.files:
                attachment.url = '{}/{}/{}'.format(
                    DVACH_URL, self.board_name, post.url_path)


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
