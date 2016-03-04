"""You need a running ElasticSearch instance bound to localhost:9200
for these tests"""
import socket
import json
from tornado.testing import AsyncTestCase, gen_test
from tornadoes import ESConnection
from tornado.iostream import IOStream

import stashpy

config = {
    'processor_spec': {'to_dict': "My name is {name} and I'm {age:d} years old."},
    'port': 8888,
    'address': 'localhost',
    'indexer_config': {'host': 'localhost',
                       'port': 9200,
                       'index_pattern': 'kita-indexer'}
}


class FindIn:
    def __init__(self, docs):
        if hasattr(docs, 'body'):
            docs = json.loads(docs.body.decode('utf-8'))
        try:
            self.docs = docs['hits']['hits']
        except KeyError:
            self.docs = docs

    def by(self, **specs):
        sentinel = object()
        return [doc for doc in self.docs
                if all(doc.get(key, sentinel) == val for key,val in specs.items())]

class StashpyTests(AsyncTestCase):

    @gen_test
    def test_indexing_line(self):
        self.es_client = ESConnection(io_loop=self.io_loop)

        app = stashpy.App(config)
        app.run()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = IOStream(s)
        yield stream.connect(("localhost", 8888))
        yield stream.write(b"My name is Yuri and I'm 6 years old.\n")
        def search_result(results):
            result_json = json.loads(results.body.decode('utf-8'))
            self.assertEqual(len(result_json['hits']['hits']), 1)
        res = yield self.es_client.search(
            search_result,
            index='kita-indexer',
            type='doc',
            source={"query": {"match_all": {}}}
        )
