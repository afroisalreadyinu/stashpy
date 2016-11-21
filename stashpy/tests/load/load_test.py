"""In order to run the load tests, start stashpy and ElasticSearch
locally and run this file"""
import os
from time import sleep
import random
import socket
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode
from datetime import datetime
from matplotlib import pyplot
import yaml
import json
import time

import stashpy
from stashpy.indexer import DEFAULT_INDEX_PATTERN

PROCESSES = ['nginx', 'uwsgi', 'python3', 'postgres', 'rabbitmq']
USERS = ['root', 'admini', 'restapi', 'postgres']
HOSTS = ['api01', 'api02', 'db', 'webserver', 'queue']
LOAD_DURATION = 5

#Why is ES query syntax so weird?

def get_config():
    filepath = os.path.abspath(os.path.join(__file__, '../config.yml'))
    with open(filepath, 'r') as conf_file:
        config = yaml.load(conf_file)
    return config

def index_url():
    index = datetime.strftime(datetime.now(), DEFAULT_INDEX_PATTERN)
    return 'http://localhost:9200/{}'.format(index)

def search_url():
    index = datetime.strftime(datetime.now(), DEFAULT_INDEX_PATTERN)
    return 'http://localhost:9200/{}/doc/_search'.format(index)


def rand_doc(base):
    vals = dict(
        process=random.choice(PROCESSES),
        host=random.choice(HOSTS),
        user=random.choice(USERS),
        duration=random.randint(1000, 50000) / 1000.0,
        output=random.randint(10, 50000)
    )
    doc = base.format(**vals)
    return doc, vals


#TODO Better living through iterators
def run_step(sock, steps, doc_base):
    docs_and_vals = [rand_doc(doc_base) for _ in range(5*steps)]
    wait_step = 5.0/(5*steps + 1)
    vals = []
    for doc,val in docs_and_vals:
        sock.sendall(doc.encode('utf-8') + b'\n')
        time.sleep(wait_step)
        vals.append(val)
    return vals

def check_step(es_host, es_port, vals):
    q = {"query": {
        "filtered": {
            "query": {"match_all": {}},
            "filter": {}}}}
    url = search_url()
    succeeded = 0
    for entry in vals:
        q['query']['filtered']['filter']['and'] = [{'term': {key: value}} for key,value in entry.items()]
        resp = urlopen(url, data=json.dumps(q).encode('utf-8'))
        hits = json.loads(resp.read().decode('utf-8'))['hits']['total']
        if hits == 1:
            succeeded += 1
    return succeeded



def main():
    config = get_config()
    try:
        urlopen(Request(index_url(), method='DELETE'))
    except HTTPError:
        pass
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config['address'], config['port']))
    per_second = list(range(0, 210, 10))
    per_second[0] = 1
    success_vals = []
    for step in per_second:
        print('Doing {} loglines per sec'.format(step))
        vals = run_step(sock, step, config['processor_spec']['to_dict'][0])
        if step == 1:
            time.sleep(2)
        resp = urlopen(Request('http://localhost:9200/stashpy-2016-03-16/_flush', urlencode({'wait_if_ongoing': 'true'}).encode('utf-8'))).read()
        success_vals.append(check_step(config['indexer_config']['host'],
                                       config['indexer_config']['port'],
                                       vals))
    pyplot.plot(per_second, success_vals)
    pyplot.xlabel('Log lines per second')
    pyplot.ylabel('Successful')
    pyplot.savefig('lines_per_sec.png', bbox_inches='tight')

if __name__ == "__main__":
    main()
