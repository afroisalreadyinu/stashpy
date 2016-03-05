import unittest
from datetime import datetime
import json

import stashpy

class IndexerTests(unittest.TestCase):

    def request_body(self, request):
        return json.loads(request.body.decode('utf-8'))

    def test_simple_indexing(self):
        indexer = stashpy.ESIndexer('localhost', 9200)
        doc = {'name':'Lilith', 'age': 4}
        request = indexer._create_request(doc)
        url_prefix = datetime.strftime(
            datetime.now(),
            'http://localhost:9200/stashpy-%Y-%m-%d/doc/'
        )
        self.assertTrue(request.url.startswith(url_prefix))
        self.assertDictEqual(self.request_body(request), doc)


    def test_index_pattern_in_doc(self):
        indexer = stashpy.ESIndexer('localhost', 9200)
        doc = {'name':'Lilith', 'age': 4, '_index_':'Kita-{name}-%Y'}
        request = indexer._create_request(doc)
        url_prefix = datetime.strftime(
            datetime.now(),
            'http://localhost:9200/Kita-Lilith-%Y/doc/'
        )
        self.assertTrue(request.url.startswith(url_prefix))
        self.assertDictEqual(self.request_body(request), doc)

    def test_index_pattern_not_date(self):
        doc = {'name':'Lilith', 'age': 4, '_index_':'Kita-{name}-2016'}
        indexer = stashpy.ESIndexer('localhost', 9200)
        request = indexer._create_request(doc)
        url_prefix = datetime.strftime(
            datetime.now(),
            'http://localhost:9200/Kita-Lilith-%Y/doc/'
        )
        self.assertTrue(request.url.startswith(url_prefix))
        self.assertDictEqual(self.request_body(request), doc)

    def test_index_pattern_different_doc_type(self):
        doc = {'name':'Lilith', 'age': 4, '_index_':'Kita-{name}-2016'}
        indexer = stashpy.ESIndexer('localhost', 9200, doc_type='alternative')
        request = indexer._create_request(doc)
        url_prefix = datetime.strftime(
            datetime.now(),
            'http://localhost:9200/Kita-Lilith-%Y/alternative/'
        )
        self.assertTrue(request.url.startswith(url_prefix))
        self.assertDictEqual(self.request_body(request), doc)
