import unittest

import stashpy

sentinel = object()

class MockEsConn:
    def __init__(self, *args):
        self.puts = []

    def put(self, index, type, uid, contents, callback):
        self.puts.append((index, type, uid, contents))
        return sentinel

class IndexerTests(unittest.TestCase):

    def test_simple_indexing(self):
        indexer = stashpy.ESIndexer('localhost', 9200, connection=MockEsConn)
        return_val = indexer.index({'name':'Lilith', 'age': 4})
        self.assertEqual(return_val, sentinel)
        index,type,uid,doc = indexer.es_connections.puts[0]
