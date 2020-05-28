#!/usr/bin/env python3

import sys
import re
import socket
from skyfield.api import Topos, load
import numpy

host = "where.satellitesabove.me"
port = 5021
ticket = "ticket{delta61914foxtrot:GIF7GSN9yqlf-LP9EJkJofsCXqG5UEmCKguoHG0L9WnrPhBL6BBsGI4wLMSDAfARAw}"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ts = load.timescale()
first_run = True

def main():
#
#
    client.connect((host, port))

    # Process Ticket
    client.recv(1024)
    client.send((ticket + "\r\n").encode())

    prepare()


def prepare():
#
#
    global client, satellite, find_date

    first_run = True
    satellites = load.tle_file('stations.txt')

    buffer = ''

    while True:
            if first_run:
                data = client.recv(4096).decode()
                buffer += data
                timedata = re.search(r"\(.*?\)", data).group(0).strip('(').strip(')').split(',')    
                origin_time = ts.utc(int(timedata[0]), int(timedata[1]), int(timedata[2]), int(timedata[3]), int(timedata[4]), float(timedata[5]))

                data = client.recv(4096).decode()
                buffer += data
                location = re.search(r"\[.*?\]", data).group(0).strip('[').strip(']').split(',')
                origin_loc = numpy.array([location[0], location[1], location[2]])

                for s in satellites:
                    geo_pos = s.at(origin_time)
                    if(round(float(geo_pos.position.km[0]), 5) == round(float(origin_loc[0]),5)):
                        if(round(float(geo_pos.position.km[1]), 5) == round(float(origin_loc[1]),5)):
                            if(round(float(geo_pos.position.km[2]), 5) == round(float(origin_loc[2]),5)):
                                satellite = s
                                break

                first_run = False


            data = client.recv(4096).decode()
            buffer += data
            buffer = ''
            process(data)


def process(data):
#
#
    global ts, satellite, find_date

    lines = data.split('\n')

    # Did we get a flag, if so let's quit.
    if re.search(r"flag{", data):
        print(data)
        sys.exit()
    
    try:
        timedata = re.search(r"\(.*?\)", lines[-2]).group(0).strip('(').strip(')').split(',')
        find_date = ts.utc(int(timedata[0]), int(timedata[1]), int(timedata[2]), int(timedata[3]), int(timedata[4]), float(timedata[5]))
    except:
        # Incomplete data from the server, return and try to receive data again.
        return

    value = (data[data.find("coordinate at") - 2])
    if value == 'X':
        index = 0
    elif value == 'Y':
        index = 1
    elif value == 'Z':
        index = 2

    geo_pos = satellite.at(find_date)
    print(f"Sending {value} Location {geo_pos.position.km[index]} for at {find_date.utc_datetime()} ")
    client.send((str(geo_pos.position.km[index]) + "\r\n").encode())

main()




