import json
import logging
import requests


class Facebook(object):
    host = 'https://graph.facebook.com/'
    logger = None

    def __init__(self, access_token):
        self.access_token = access_token
        self.logger = logging.getLogger(__name__)

    def profile(self):
        url = self.host + 'me?fields=id,name,movies{name,genre},age_range,picture{url},email&access_token=' + self.access_token
        return self._open(url)

    def _open(self, url):
        try:
            response = requests.get(url)
        except Exception, e:
            self.logger.error(e)
            self.logger.error(url)

        response.connection.close()

        # Validate the response
        res = {}
        try:
            res = response.json()
        except (ValueError, AttributeError):
            e = 'Invalid JSON response from Facebook'
            self.logger.error(e)
            self.logger.error(response.body)
        finally:
            return res


