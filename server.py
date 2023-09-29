#  coding: utf-8 
import socketserver
import os 
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle_file(self, file_path):
            # Handles a single file request. Sends either a 200 OK or a 404 FILE NOT FOUND Error 
            if os.path.isfile(file_path):
                content = open(file_path, 'rb').read()
                content_type = 'text/' + file_path.split('.')[-1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode("utf-8") + content
                print("200 OK at Path %s\n" % file_path)
                self.request.sendall(response)                
            else:
                print("404 ERROR: File not Found at %s\n" % file_path) 
                self.request.sendall(f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n filepath {file_path} does not exist".encode("utf-8"))
                
                
    def handle(self):
        #self.request is the TCP Socket we are handling  
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s" % self.data)
         
        # Decodes and splits the request recieved from the socket 
        req = self.data.decode('utf-8') 
        req_lines = req.split('\r\n') 
        req_method= req_lines[0].split()[0]
        req_path = req_lines[0].split()[1]
        
        
        if req_method == 'GET':
            
            # Turn requests into the file_path 
            if req_path == "/": req_path = "/index.html"
            file_path = "www"+req_path
            
            # Security handling, the directory request MUST be in the current working directory (./www)
            if not os.path.realpath(file_path).startswith(os.getcwd()):
                self.request.sendall(f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n filepath {file_path} does not exist".encode("utf-8"))
                print ("Error 404: Unauthorized Access for Path  %s\n" % file_path)
                
            # Handle a file request 
            elif os.path.isfile(file_path): 
                content = open(file_path, 'rb').read()
                content_type = 'text/' + file_path.split('.')[-1]
                response = f"HTTP/1.1 200 OK \r\nContent-Type:{content_type}\r\n\r\n".encode("utf-8") + content
                print("200 OK at Path %s\n" % file_path)
                self.request.sendall(response)
            
            # Handle Redirect Requests (Current request path points to no file or directory) 
            elif not req_path.endswith("/"):
                redirect_url = "http://127.0.0.1:8080" + f"{req_path}" + "/"          
                response = f"HTTP/1.1 301 Permanent Redirect\r\nLocation:{redirect_url}\r\n\r\n".encode("utf-8")
                print("301 REDIRECT to Path %s\n" % file_path) 
                self.request.sendall(response)
                
                file_path += "/index.html"
                self.handle_file(file_path)
                
            # Handle Directories 
            elif os.path.isdir(file_path):
                file_path +="index.html"
            
                self.handle_file(file_path)
            # Handle all other instances of requests 
            else:
                print("404 ERROR: File not Found at %s\n" % file_path) 
                self.request.sendall(f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n filepath {file_path} does not exist".encode("utf-8"))
            
        else:
             # Handle other requests and return a 404 error
             print("405 ERROR: Method request is not supported") 
             self.request.sendall(b"HTTP/1.1 405 Method not allowed \r\n\r\n")
        
        
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
