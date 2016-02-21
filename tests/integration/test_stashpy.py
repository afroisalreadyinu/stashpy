"""You need a running ElasticSearch instance bound to localhost:9200
for these tests"""

from tornado.testing import AsyncTestCase


class StashpyTests(AsyncTestCase):

    def test_indexing_line(self):
        pass
