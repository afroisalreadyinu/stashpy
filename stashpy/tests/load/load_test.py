"""In order to run the load tests, start stashpy and ElasticSearch
locally and run this file"""
from time import sleep
import random
import socket
#from matplotlib import pyplot
import yaml

BASE = "Process {process} on {host} worked for {duration} secs and produced {output} bytes output for user {user}"

PROCESSES = ['nginx', 'uwsgi', 'python3', 'postgres', 'rabbitmq']
USERS = ['root', 'admini', 'restapi', 'postgres']
HOSTS = ['api01', 'api02', 'db', 'webserver', 'queue']

def rand_doc():
    return BASE.format(
        process=random.choice(PROCESSES),
        host=random.choice(HOSTS),
        user=random.choice(USERS),
        duration=random.randint(1000, 50000) / 1000.0,
        output=random.randint(10, 50000)
    )


def run_step(sock, steps):
    docs = [rand_doc() for _ in range(steps+1)]
    wait_step = 1.0/steps
    total_wait = 0
    while total_wait < 1:
        doc = docs.pop()
        sock.sendall(doc.encode('utf-8') + b'\n')
        total_wait += wait_step
    return docs

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8888))
    per_second = list(range(0, 40, 10))
    per_second[0] = 1
    for step in per_second:
        docs = run_step(sock, step)
        check_step(docs)

if __name__ == "__main__":
    main()
