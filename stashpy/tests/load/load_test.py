"""In order to run the load tests, start stashpy and ElasticSearch
locally and run this file"""
import os
from time import sleep
import random
import socket
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from datetime import datetime
#from matplotlib import pyplot
import yaml
import json
import time

import stashpy

PROCESSES = ['nginx', 'uwsgi', 'python3', 'postgres', 'rabbitmq']
USERS = ['root', 'admini', 'restapi', 'postgres']
HOSTS = ['api01', 'api02', 'db', 'webserver', 'queue']

#Why is ES query syntax so weird?

def get_config():
    filepath = os.path.abspath(os.path.join(__file__, '../config.yml'))
    with open(filepath, 'r') as conf_file:
        config = yaml.load(conf_file)
    return config

def index_url():
    index = datetime.strftime(datetime.now(), stashpy.DEFAULT_INDEX_PATTERN)
    return 'http://localhost:9200/{}'.format(index)

def search_url():
    index = datetime.strftime(datetime.now(), stashpy.DEFAULT_INDEX_PATTERN)
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


def run_step(sock, steps, doc_base):
    docs_and_vals = [rand_doc(doc_base) for _ in range(steps+1)]
    docs = [x[0] for x in docs_and_vals]
    vals = [x[1] for x in docs_and_vals]
    wait_step = 1.0/steps
    submitted = 0
    while submitted < steps:
        doc = docs.pop()
        sock.sendall(doc.encode('utf-8') + b'\n')
        submitted += 1
    return vals

def check_step(es_host, es_port, vals):
    q = {"query": {
        "filtered": {
            "query": {"match_all": {}},
            "filter": {}}}}
    url = search_url()
    time.sleep(5)
    for entry in vals:
        q['query']['filtered']['filter']['and'] = [{'term': {key: value}} for key,value in entry.items()]
        resp = urlopen(url, data=json.dumps(q).encode('utf-8'))
        hits = json.loads(resp.read().decode('utf-8'))['hits']['total']
        print(hits)


def main():
    config = get_config()
    try:
        urlopen(Request(index_url(), method='DELETE'))
    except HTTPError:
        pass
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config['address'], config['port']))
    per_second = list(range(0, 40, 10))
    per_second[0] = 1
    for step in per_second:
        vals = run_step(sock, step, config['processor_spec']['to_dict'][0])
        check_step(config['indexer_config']['host'],
                   config['indexer_config']['port'],
                   vals)

if __name__ == "__main__":
    main()
