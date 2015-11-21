"""Random OP images from index page."""

import random
import webbrowser

from chan.api import Page

# get images from nulch
initial_posts = [thread.original_post for thread in Page('b', 0).threads]

attachments = [initial_post.files[0].url
               for initial_post in initial_posts
               if initial_post.files[0].is_picture()]

pic = random.choice(attachments)

print 'roll is', pic
try:
    webbrowser.open(pic)
except Exception, e:
    print 'Check webbrowser settings!'
