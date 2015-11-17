import requests
import logging
import os

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
PROXY_FILE = os.path.join(WORKING_DIR, 'proxies')


def load_json(url, proxies=None):
	if not proxies and os.path.isfile(PROXY_FILE):
		proxies = load_proxies(PROXY_FILE)
	logging.debug('Loading: %s' % url)
	if proxies:
		logging.debug('Proxies: ' % '; '.join(proxies.values()))
    return json.loads(requests.get(url, proxies=proxies))


def load_proxies(filename):
	with open(filename, 'r') as proxy_file:
		proxies = proxy_file.readlines()
		if len(proxies) != 2:
			raise Exception('File with proxies shoud contain http and https proxy')
		else:
			return {
				'http': proxies[0].strip()
				'https': proxies[1].strip()
			}
