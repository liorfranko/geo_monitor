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


def latency(dest_name):
    try:
        start = time.time()
        response = requests.get(dest_name,timeout=5)
        roundtrip = time.time() - start
        if response.status_code == 200:
            return roundtrip
        else:
            print "Error, response conde isn't 200"
    except KeyboardInterrupt:
        print "Bye bye..."
        sys.exit(1)
    except:
        return 5
dict = {}
while (True):
    try:
        print "{:<50} {:30} {:>10}".format('Name','Current Latency','Last 20 Average Latency')
        for server in yaml_file['latency']:
            url = server['url']
            name = server['name']
            let = latency(url)
            if not url in dict:
                dict[url]=deque([let])
            else:
                if len(dict[url]) > 20:
                    dict[url].popleft()
                    dict[url].append(let)
                else:
                    dict[url].append(let)
            if let > 2:
                print bcolors.FAIL + "{:<50} {:30} {:>10}".format(name, str(let), sum(dict[url])/len(dict[url])) + bcolors.ENDC
            elif let > (sum(dict[url])/len(dict[url])):
                print bcolors.WARNING + "{:<50} {:30} {:>10}".format(name, str(let), sum(dict[url])/len(dict[url])) + bcolors.ENDC
            else:
                print bcolors.OKGREEN + "{:<50} {:30} {:>10}".format(name, str(let), sum(dict[url])/len(dict[url])) + bcolors.ENDC
        print "-----------------------------------------------------------------------------------------------------------------------------"
    except KeyboardInterrupt:
        print "Bye bye..."
        sys.exit(1)

