__author__ = 'liorf'
import yaml
import time
import requests
import sys
from collections import deque


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def open_yaml():
    with open("geo_conf.yaml", 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print (exc)


yaml_file = open_yaml()


def latency(dest_name, timeout):
    try:
        start = time.time()
        response = requests.get(dest_name, timeout=timeout)
        roundtrip = time.time() - start
        if response.status_code == 200:
            return roundtrip * 1000
        else:
            print "Error, response conde isn't 200"
    except KeyboardInterrupt:
        print "Bye bye..."
        sys.exit(1)
    except:
        return 5


latency_dict = {}
TIMEOUT = yaml_file['timeout']
AVERAGE = yaml_file['average']
WARNING_TIME = yaml_file['warning_time']

while True:
    try:
        print "{:<50} {:30} {:>10}".format('Name', 'Current Latency', 'Average Latency')
        for server in yaml_file['latency']:
            url = server['url']
            name = server['name']
            let = latency(url, TIMEOUT)
            if url not in latency_dict:
                latency_dict[url] = deque([let])
            else:
                if len(latency_dict[url]) > AVERAGE:
                    latency_dict[url].popleft()
                    latency_dict[url].append(let)
                else:
                    latency_dict[url].append(let)
            if type(latency_dict[url][0]) is str:
                print 'int'
            if let > WARNING_TIME:
                print bcolors.FAIL, \
                    "{:<50} {:30} {:>10}".format(name,
                                                 "{0:.3f}ms".format(let), "{0:.3f}ms".format(
                            round(sum(latency_dict[url]) / len(latency_dict[url]), 2))), bcolors.ENDC
            elif let > (sum(latency_dict[url]) / len(latency_dict[url])):
                print bcolors.WARNING, "{:<50} {:30} {:>10}".format(name,
                                                                    "{0:.3f}ms".format(let),
                                                                    "{0:.3f}ms".format(round(
                                                                        sum(latency_dict[url]) / len(latency_dict[url]),
                                                                        2))), bcolors.ENDC
            else:
                print bcolors.OKGREEN, "{:<50} {:30} {:>10}".format(name,
                                                                    "{0:.3f}ms".format(let),
                                                                    "{0:.3f}ms".format(round(sum(latency_dict[url]) /
                                                                                             len(latency_dict[url]),
                                                                                             2))), bcolors.ENDC
        print "-" * 129
    except KeyboardInterrupt:
        print "Bye bye..."
        sys.exit(1)
