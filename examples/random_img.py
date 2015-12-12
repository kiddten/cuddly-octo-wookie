"""Random OP images from index page."""

import random
import webbrowser
import pyperclip
from collections import namedtuple

from abu import Page


Pic = namedtuple('Pic', 'op thread')

# get images from nulch
images = [Pic(thread.original_post, thread.url)
          for thread in Page('b', 0)]

attachments = [(pic.op.attachments[0].url, pic.thread)
               for pic in images
               if pic.op.attachments[0].is_picture()]

pic = random.choice(attachments)
content = 'pic\n{}\nthread\n{}'.format(*pic)
print content

try:
    pyperclip.copy(content)
except:
    print 'Check pyperclip settings!'

try:
    webbrowser.open(pic[0])
except Exception, e:
    print 'Check webbrowser settings!'
