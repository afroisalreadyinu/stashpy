from uuid import uuid4
from datetime import datetime
import json
import logging

import tornado.httpclient
from tornado import gen

logger = logging.getLogger(__name__)

DEFAULT_INDEX_PATTERN = "stashpy-%Y-%m-%d"

class ESIndexer:

    def __init__(self, host, port, index_pattern=DEFAULT_INDEX_PATTERN, doc_type='doc'):
        self.base_url = 'http://{}:{}'.format(host, port)
        self.client = tornado.httpclient.AsyncHTTPClient()
        self.index_pattern = index_pattern
        self.doc_type = doc_type

    def _create_request(self, doc):
        doc_id = str(uuid4())
        index = datetime.strftime(datetime.now(),
                                  doc.pop('_index_', self.index_pattern))
        if '{' in index and '}' in index:
            index = index.format(**doc)
        url = self.base_url + "/{}/{}/{}".format(index, self.doc_type, doc_id)
        return tornado.httpclient.HTTPRequest(url, method='POST', headers=None, body=json.dumps(doc))

    @gen.coroutine
    def index(self, doc):
        request = self._create_request(doc)
        response = yield self.client.fetch(request)
        if 200 <= response.code < 300:
            logger.info("Successfully indexed doc, url: {}".format(
                response.effective_url))
        else:
            logger.warn("Index request returned response {}, reason: {}".format(
                response.code,
                response.reason))
