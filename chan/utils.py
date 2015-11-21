import requests
import logging
import json
import os

from requests.exceptions import ConnectionError

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
PROXY_FILE = os.path.join(WORKING_DIR, 'proxies')


def load_json(url, proxies=None):
    if not proxies and os.path.isfile(PROXY_FILE):
        proxies = load_proxies(PROXY_FILE)
    logging.debug('Loading: %s', url)
    if proxies:
        logging.debug('Proxies: %s', '; '.join(proxies.values()))
    return json.loads(requests.get(url, proxies=proxies).content)


def ping(url, proxies=None):
    if not proxies and os.path.isfile(PROXY_FILE):
        proxies = load_proxies(PROXY_FILE)
    try:
        response = requests.get(url, proxies=proxies)
        return response.status_code == 200
    except ConnectionError:
        return False


def load_proxies(filename):
    with open(filename, 'r') as proxy_file:
        proxies = proxy_file.readlines()
        if len(proxies) != 2:
            raise Exception(
                'File with proxies shoud contain http and https proxy')
        else:
            return {
                'http': proxies[0].strip(),
                'https': proxies[1].strip()
            }
