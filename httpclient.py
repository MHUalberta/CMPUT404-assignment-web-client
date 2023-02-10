#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        header = self.get_headers(data)
        code = int(re.findall("HTTP/1\.[0|1] ([0-9]+)", header)[0])  #Extract the code, for some reason also getting HTTP 1.0 responses so I have to account for that with a [0|1] in my regex
        return code

    def get_headers(self, data):
        response_split = data.split("\r\n\r\n", 1)  #divide the response into [headers, body]
        headers = response_split[0]
        return headers

    def get_body(self, data):
        response_split = data.split("\r\n\r\n", 1)  #divide the response into [headers, body]
        body = response_split[1] if len(response_split) > 1 else ""
        return body

    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()


    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

        
    def send_request(self, url, command ,args=None):
        #Parse URL using urllib
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = 80 if (parsed_url.scheme=="http" and parsed_url.port==None) else parsed_url.port     #If port is omitted, specify port 80 (HTTP default port)
        path = "/" if (parsed_url.path=="") else parsed_url.path                                    #If path is omitted, specify path to root
            
        #Connect to the host
        self.connect(host, port)

        if command == "POST":
            #Encode the args if provided
            data = urllib.parse.urlencode(args) if (args!=None) else ""  
            #Build POST request
            request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(data)}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{data}"
        
        else:
            #Build GET request
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        
        self.sendall(request)


    def handle_response(self):
        #Wait for response and close on arrival
        response = self.recvall(self.socket)
        self.close()

        #Parse response
        code = self.get_code(response)
        body = self.get_body(response)
        return code, body


    def GET(self, url, args=None):
        self.send_request(url, "GET")
        code, body = self.handle_response()
        return HTTPResponse(code, body)
    

    def POST(self, url, args=None):
        self.send_request(url, "POST", args)
        code, body = self.handle_response()
        return HTTPResponse(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
