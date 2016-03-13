"""In order to run the load tests, start stashpy and ElasticSearch
locally and run this file"""
import os
from time import sleep
import random
import socket
from urllib.request import urlopen
#from matplotlib import pyplot
import yaml

PROCESSES = ['nginx', 'uwsgi', 'python3', 'postgres', 'rabbitmq']
USERS = ['root', 'admini', 'restapi', 'postgres']
HOSTS = ['api01', 'api02', 'db', 'webserver', 'queue']

def get_config():
    filepath = os.path.abspath(os.path.join(__file__, '../config.yml'))
    with open(filepath, 'r') as conf_file:
        config = yaml.load(conf_file)
    return config

def rand_doc(base):
    return base.format(
        process=random.choice(PROCESSES),
        host=random.choice(HOSTS),
        user=random.choice(USERS),
        duration=random.randint(1000, 50000) / 1000.0,
        output=random.randint(10, 50000)
    )


def run_step(sock, steps, doc_base):
    docs = [rand_doc(doc_base) for _ in range(steps+1)]
    wait_step = 1.0/steps
    total_wait = 0
    while total_wait < 1:
        doc = docs.pop()
        sock.sendall(doc.encode('utf-8') + b'\n')
        total_wait += wait_step
    return docs

def check_step(es_host, es_port, docs):
    for doc in docs:
        pass

def main():
    config = get_config()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config['address'], config['port']))
    per_second = list(range(0, 40, 10))
    per_second[0] = 1
    for step in per_second:
        docs = run_step(sock, step, config['processor_spec']['to_dict'][0])
        check_step(config['indexer_config']['host'],
                   config['indexer_config']['port'],
                   docs)

if __name__ == "__main__":
    main()
