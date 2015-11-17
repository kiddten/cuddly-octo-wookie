import json
import utils

DVACH_URL = 'http://2ch.hk'


class Thread:

    def __init__(self, json, board_name):
        self.board_name = board_name
        self.posts = []
        self.__parse_json(json)
        self.__create_urls()

    def __parse_json(self, json):
        self.files_count = json['files_count']
        self.posts_count = json['posts_count']
        self.id = json['thread_num']

    def __create_urls(self):
        self.url = '{}/{}/res/{}.html'.format(
            DVACH_URL, self.board_name, self.id)
        self.url_json = '{}/{}/res/{}.json'.format(
            DVACH_URL, self.board_name, self.id)

    def load(self):
        thread_json = utils.load_json(self.url_json)
        self.title = thread_json['threads'][0]['title']
        for post in thread_json['threads'][0]['posts']:
            self.posts.append(Post(post))
        # create absolute links of files
        for post in self.posts:
            for attachment in post.files:
                attachment.url = '{}/{}/{}'.format(
                    DVACH_URL, self.board_name, post.url_path)


class Post:

    def __init__(self, json):
        self.files = []
        self.__parse_json(json)

    def __parse_json(self, json):
        self.text = json['comment']
        for f in json['files']:
            self.files.append(AttachedFile(f))


class AttachedFile:

    def __init__(self, json):
        self.__parse_json(json)

    def is_picture(self):
        return self.name.endswith('.jpg')

    def is_webm(self):
        return self.name.endswith('.webm')

    def __parse_json(self, json):
        self.type = json['type']
        self.name = json['name']
        self.size = int(json['size'])
        self.url_path = json['path']
        self.url = ''
