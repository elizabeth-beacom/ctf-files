#!/usr/bin/env python3

import sys
import socket
import select


host = "stars.satellitesabove.me"
port = 5013
ticket = "ticket{november40927tango:GOf3S35BwbIJQb7RLocpJH9s1PS8Fv5PnD80iyAOHJpvMK01Lv3vUn1ybb12MYY8NQ}"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
x = 0     
found_stars = []
    
def main():
    global client, x, found_stars


    client.connect((host, port))
    select.select([client], [], []) #block for reading
    # Process Ticket
    client.recv(1024)
    client.send((ticket + "\r\n").encode())

    # Main Loop
    buffer = ''
    data = ''

    while True:
        part =''

        # Retrieve Data
        # this is blocking...
        try:
            client.settimeout(2)
            data = client.recv(1024).decode()
            if len(data) < 200:
                print(data)
        except socket.timeout:
                for star in found_stars:
                    client.send(f"{star[0]},{star[1]}\r\n".encode())
                    print(f"Sending Data {star[0]},{star[1]}")
                client.send("\r\n".encode())
                print("Completing Entry...")
                found_stars = []
                x = 0
                continue
        
        if not data:
            print("Disconnected")
            sys.exit()
        else:
            buffer += data
            last_newline_index = buffer.rfind('\n')     

            part = buffer[:last_newline_index]
            buffer = buffer[last_newline_index+1:]      

            process_buffer(part) 


def process_buffer(buffer):
    global client, x

    lines = buffer.split('\n')

    # Process Information

    for line in lines:
        y = 0
        pixels = line.split(',')

        # skip empty line
        if len(pixels) <= 1 :
            break

        for pixel in pixels:
            if int(pixel) > 20:
                # Found first star
                if len(found_stars) == 0:
                    found_stars.append([x, y, int(pixel)])
                else:
                    # If current star is close to any of the other stars
                    updated_star = False
                    for star in found_stars:
                        ## current line and within 2 pixels on y -OR- on same y and within 2 pixels on x with a current star
                        if (star[0] == x and star[1] + 2 >= y) or (star[0] + 2 >= x and (star[1] + 2 >= y and star[1] - 2 <= y)):
                            updated_star = True
                            if star[2] <= int(pixel):
                                # if pixel is brighter set it.
                                found_stars.remove(star)
                                found_stars.append([x, y, int(pixel)])
                                break
                    
                    if not updated_star:
                        found_stars.append([x,y, int(pixel)])

            y += 1
        x += 1

main()
