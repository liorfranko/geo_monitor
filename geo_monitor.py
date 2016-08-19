__author__ = 'liorf'
import requests
import json
from optparse import OptionParser
import yaml
import time
import socket
import struct

def trace(dest_name):
    hops = []
    dest_addr = socket.gethostbyname(dest_name)
    print 'Starting traceroute to: ' + dest_name
    print 'Resolve IP is: ' + dest_addr
    port = 33434
    max_hops = 30
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1
    while True:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        # Build the GNU timeval struct (seconds, microseconds)
        timeout = struct.pack("ll", 5, 0)

        # Set the receive timeout so we behave more like regular traceroute
        recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

        recv_socket.bind(("", port))
        #sys.stdout.write(" %d  " % ttl)
        send_socket.sendto("", (dest_name, port))
        curr_addr = None
        curr_name = None
        finished = False
        tries = 1
        while not finished and tries > 0:
            try:
                _, curr_addr = recv_socket.recvfrom(512)
                finished = True
                curr_addr = curr_addr[0]
                try:
                    curr_name = socket.gethostbyaddr(curr_addr)[0]
                except socket.error:
                    curr_name = curr_addr
            except socket.error as (errno, errmsg):
                tries = tries - 1
                hops.append("*")

        send_socket.close()
        recv_socket.close()

        if not finished:
            pass

        if curr_addr is not None:
            curr_host = "%s (%s)" % (curr_name, curr_addr)
        else:
            curr_host = ""
        for dc in yaml_file['datacerters']:
            if curr_addr == dc['ip']:
                print 'Going to DC: ' + dc['dc']
                print 'ASR IP: ' + dc['ip']
                print 'ISP is: ' + dc['isp']
                return
        hops.append(curr_host)

        ttl += 1
        if curr_addr == dest_addr or ttl > max_hops:
            print 'Traceroute failed hops are:'
            for hop in hops:
                print hop
            break


def geo(dest_name):
    print "I'm coming from:"
    response = requests.get(dest_name)
    if response.status_code < 400:
        response_obj = json.loads(response.text)
        print json.dumps(response_obj, indent=4)

def latency(dest_name):
    print "Starting latency test of " + dest_name
    start = time.time()
    response = requests.get(dest_name)
    roundtrip = time.time() - start
    if response.status_code == 200:
        print "It took me: " + str(roundtrip)
    else:
        print "Error, response conde isn't 200"

def option_parser():
    parser = OptionParser()
    parser.add_option("-t", "--traceroute",
                      help="Show tracerotue",
                      action="store_true", dest="trace")
    parser.add_option("-l", "--latency",
                      help="Show latency",
                      action="store_true", dest="latency")
    parser.add_option("-g", "--geo",
                      help="Show geolocation information",
                      action="store_true", dest="geo")
    parser.add_option("-n", "--name",
                      help="The service name",type="string",
                      action="store", dest="dest_name")
    parser.add_option("-u", "--url",
                      help="The url",type="string",
                      action="store", dest="url_name")
    (options, args) = parser.parse_args()
    return options

def open_yaml():
    with open("geo_conf.yaml", 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)


yaml_file = open_yaml()
options = option_parser()

if options.geo:
    geo(yaml_file['geo_api_url'])
if options.trace:
    for server in yaml_file['latency']:
        trace(server['name'])
if options.latency:
    for server in yaml_file['latency']:
        latency(server['url'])


print "Done"