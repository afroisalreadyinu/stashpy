"""You need a running ElasticSearch instance bound to localhost:9200
for these tests"""
import socket
import json
from urllib.parse import urlencode

from tornado.testing import AsyncTestCase, gen_test
from tornado.iostream import IOStream
from tornado.httpclient import AsyncHTTPClient
import tornado.gen

import stashpy

config = {
    'processor_spec': {'to_dict': ["My name is {name} and I'm {age:d} years old."]},
    'port': 8888,
    'address': 'localhost',
    'es_config': {'host': 'localhost',
                  'port': 9200,
                  'index_pattern': 'kita-indexer'}
}

def decode(resp):
    return json.loads(resp.body.decode('utf-8'))

class FindIn:
    def __init__(self, docs):
        if hasattr(docs, 'body'):
            docs = decode(docs)
        try:
            self.docs = docs['hits']['hits']
        except KeyError:
            self.docs = docs

    def by(self, **specs):
        sentinel = object()
        return [doc for doc in self.docs
                if all(doc['_source'].get(key, sentinel) == val for key,val in specs.items())]

class StashpyTests(AsyncTestCase):

    @gen_test
    def test_indexing_line(self):
        client = AsyncHTTPClient()
        ping = yield client.fetch("http://localhost:9200/", raise_error=False)
        if ping.code != 200 or decode(ping)['tagline'] != "You Know, for Search":
            self.fail("This test requires an ES instance running on localhost")

        #delete if existing
        url = "http://localhost:9200/{}/".format(config['es_config']['index_pattern'])
        resp = yield client.fetch(url, method='DELETE', headers=None, raise_error=False)

        app = stashpy.App(config)
        app.run()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = IOStream(s)
        yield stream.connect(("localhost", 8888))
        yield stream.write(b"My name is Yuri and I'm 6 years old.\n")

        yield tornado.gen.sleep(2)
        params = urlencode({'name': 'Yuri'})
        url = "http://localhost:9200/kita-indexer/doc/_search?q=" + params
        resp = yield client.fetch(url)
        resp_hits = json.loads(resp.body.decode('utf-8'))['hits']['hits']
        self.assertEqual(len(FindIn(resp).by(name='Yuri')), 1)
