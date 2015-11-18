import json
import utils

DVACH_URL = 'http://2ch.hk'


class Thread(object):

    def __init__(self, data, board_name):
        self.board_name = board_name
        self.posts = []
        self.__parse_json(data)
        self.__create_urls()

    def __parse_json(self, data):
        self.files_count = int(data['files_count'])
        self.posts_count = int(data['posts_count'])
        self.id = data['thread_num']
        self.original_post = Post(data['posts'][0])

    def __create_urls(self):
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
        self.__parse_json(data)

    def __parse_json(self, data):
        self.message = data['comment']
        for f in data['files']:
            self.files.append(AttachedFile(f))


class AttachedFile(object):

    def __init__(self, data):
        self.url = ''
        self.__parse_json(data)

    def is_picture(self):
        return self.name.endswith('.jpg')

    def is_webm(self):
        return self.name.endswith('.webm')

    def __parse_json(self, data):
        self.type = data['type']
        self.name = data['name']
        self.size = int(data['size'])
        self.url_path = data['path']

