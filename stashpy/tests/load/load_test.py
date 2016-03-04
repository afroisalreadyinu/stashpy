"""In order to run the load tests, start stashpy and ElasticSearch
locally and run this file"""
from time import time

def shoot(gap, duration):
    _sum = 0
    while _sum < duration:
        #shoot message
        time.sleep(gap)
        _sum += gap

def main():
    msgs_per_sec = [x*10 for x in range(1,100)]
    for per_sec in msgs_per_sec:
        gap = 1.0 / per_sec


if __name__ == "__main__":
    main()
