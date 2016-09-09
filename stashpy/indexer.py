from uuid import uuid4
from datetime import datetime
import json
import logging

import tornado.httpclient
from tornado import gen

logger = logging.getLogger(__name__)

DEFAULT_INDEX_PATTERN = "stashpy-%Y-%m-%d"
TEMPLATE_NAME = 'stashpy_template'
INDEX_TEMPLATE = {
  "template" : "*",
  "settings" : {
    "index.refresh_interval" : "5s"
  },
  "mappings" : {
    "_default_" : {
      "_all" : {"enabled" : True, "omit_norms" : True},
      "dynamic_templates" : [ {
        "message_field" : {
          "match" : "message",
          "match_mapping_type" : "string",
          "mapping" : {
            "type" : "string", "index" : "analyzed", "omit_norms" : True,
            "fielddata" : { "format" : "disabled" }
          }
        }
      }, {
        "string_fields" : {
          "match" : "*",
          "match_mapping_type" : "string",
          "mapping" : {
            "type" : "string", "index" : "analyzed", "omit_norms" : True,
            "fielddata" : { "format" : "disabled" },
            "fields" : {
              "raw" : {"type": "string", "index" : "not_analyzed", "ignore_above" : 256}
            }
          }
        }
      } ],
      "properties" : {
        "@timestamp": { "type": "date" },
        "@version": { "type": "string", "index": "not_analyzed" },
        "geoip"  : {
          "dynamic": True,
          "properties" : {
            "ip": { "type": "ip" },
            "location" : { "type" : "geo_point" },
            "latitude" : { "type" : "float" },
            "longitude" : { "type" : "float" }
          }
        }
      }
    }
  }
}


class ESIndexer:

    def __init__(self, host, port, index_pattern=DEFAULT_INDEX_PATTERN, doc_type='doc'):
        self.base_url = 'http://{}:{}'.format(host.rstrip('/'), port)
        self.client = tornado.httpclient.AsyncHTTPClient()
        self.index_pattern = index_pattern
        self.doc_type = doc_type
        self._check_template()

    @gen.coroutine
    def _check_template(self):
        #see whether there is a template
        url = self.base_url + "/_template/"
        request = tornado.httpclient.HTTPRequest(url, method='GET', headers=None)
        response = yield self.client.fetch(request)
        templates = json.loads(response.body.decode('utf-8'))
        if 'stashpy_template' in templates:
            return
        url = self.base_url + "/_template/{}/".format(TEMPLATE_NAME)
        request = tornado.httpclient.HTTPRequest(url, method='PUT', headers=None, body=json.dumps(INDEX_TEMPLATE))
        response = yield self.client.fetch(request)
        ack = json.loads(response.body.decode('utf-8'))
        #TODO check ack


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
            logger.debug("Successfully indexed doc, url: {}".format(
                response.effective_url))
        else:
            logger.info("Index request returned response {}, reason: {}".format(
                response.code,
                response.reason))
