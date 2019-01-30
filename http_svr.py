"""The purpose of this program is to run a basic web server that can respond to GET requests from http_cli.py, PostMan, or a web browser.
It will than determine if the GET request is valid, if so will return the page at the provided path with a response of 200 OK.  
If the request is anything other than a GET it will return error code 501.  If the URL provided does not correspond to a file path on 
server it will respond with 404.  If the URL contains a bad request containing /../ it will respond with 400 and if there is a server 
error it will respond with 500 to prevent unauthorized file access

USE: python3 http_svr.py PORT (PORT RANGE FOR STUDENT IS 10540-10559)


Note:  When using a web browser the server may respond twice, the first is the actual
request/response and the second will be a 404 Not Found.  This is due to favicon implementation on web browsers
They send 2 requests, the first is the URL GET request, the second request is for  favicon.ico.  Since this servers 
web_root currently does not contain a favicon.ico that is why a 200 OK will be followed a 404.
"""

import socket
import sys
import select
import os
from datetime import datetime
import time
import mimetypes

MIN_PORT = 10540
MAX_PORT = 10559
HOST = None
PORT = None
sock = None

#Create base header and print out response type on server console
def create_header(code):
    header =''

    if(code == 200):
        header ='HTTP/1.1 200 OK\r\n'


    elif(code == 400):
        header ='HTTP/1.1 400 Bad Request\r\n'


    elif(code == 404):
        header = 'HTTP/1.1 404 Not Found\r\n'
        

    elif(code == 500):
        header ='HTTP/1.1 500 Internal Server Error\r\n'
        

    elif(code == 501):
        header ='HTTP/1.1 501 Not Implemented\r\n'
        

    #Append header with serverDatetime and connection close
    serverTime = time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.localtime())
    header += 'Date: ' + serverTime + '\r\n'
    header += 'Connection: close\r\n' 
    return header


if __name__ == "__main__":

    #Verify that only 1 arguement provided
    if(int(len(sys.argv) > 2)):
        sys.stderr.write("Excessive arguements provided, please only provide port number\n")
        sys.exit(1)

    #Verify that commandline arguement for PORT provided otherwise exit
    try:
        argString = sys.argv[1]
    except IndexError:
        sys.stderr.write("No Command Line Arguement Provided, Exiting\n")
        sys.stderr.write("Use: python3 http_svr.py PORT")
        sys.exit(1)


    #Verify commandline arguement is a PORT number assigned to Dave Pannu
    #and not malformed, otherwise exit
    try:
        PORT = int(sys.argv[1])
        if not (MIN_PORT <= PORT <=  MAX_PORT):
            sys.stderr.write("Port number out of range, use values between 10540 and 10559\n")
            sys.exit(1)
    except ValueError:
        sys.stderr.write("Invalid port number format, exiting\n")
        sys.exit(1)

    #Create socket, bind socket, listen on socket
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            sock = socket.socket(af, socktype, proto)
        except OSError as msg:
            sock = None
            continue
        try:
            sock.bind(sa)
            sock.listen(1)
        except OSError as msg:
            sock.close()
            sock = None
            continue
        break
    if sock is None:
        print('Unable to open Socket. Exiting\n')
        sys.exit(1)


    #Main Server loop
    while True:
        print("Waiting for Connection")
        #Accept connection
        conn, addr = sock.accept()
        print('Connected to', addr)

        #While loop to recieve binary header until \r\n\r\n from socket
        endOfHeader = b'\r\n\r\n'
        data = b''
        try:
            while endOfHeader not in data:
                pieces = conn.recv(1)
                if not pieces: break
                data += pieces
        except OSError:
            sys.stderr.write("Error recieving from socket, exiting program\n")
            sys.exit(1)


        #Decode request header
        request = data.decode()
        

        #Splits header at space between METHOD and PATH, takes index 0 and assign it to requestmethod
        requestMethod = request.split(' ')[0]


        #Split request and takes PATH from index 1 and assigns it to httpPath
        httpPath = request.split(' ')[1]


        #If provided any method other than GET provide 501 error
        #and close connection to client
        if (requestMethod != 'GET'):
            response = create_header(501)
            response += '\r\n\r\n'
            response = response.encode()
            conn.sendall(response)
            conn.close()
    
        #Else if path contains /../ Returns 400 Error
        #and closes connection to client
        elif(httpPath.find('..') != -1):
            response = create_header(400)
            response += '\r\n\r\n'
            response = response.encode()
            conn.sendall(response)
            conn.close()

        ##Else if requestmethod is a GET enter 
        elif(requestMethod == 'GET'):
            systemPath =''

            #If path is '/' assigns systemPath to path to http_svr.py location and appends web_root/index.html to it
            #EG: http://cs1.seattleu.edu:10540/ -> systemPath = home/st/pannud/p1b + /web_root/index.html
            if(httpPath == '/'):
                systemPath = sys.path[0] + '/web_root/index.html'
        

            #Else if httpPath is a valid system directory within server folder but no file provided 
            #assigns systemPath to path to http_svr.py location + /web_root + httpPath + index.html
            #EG; http://cs1.seattleu.edu:10540/foo -> systemPath = home/st/pannud/p1b/web_root/foo/index.html
            elif(os.path.isdir(sys.path[0] +'/web_root' + httpPath) == True):
                #If the URL didn't contain a '/' at the end, appends it to URL
                if(httpPath.endswith('/') == False):
                  httpPath = httpPath + '/'
                systemPath = sys.path[0] + '/web_root' + httpPath + 'index.html'


            #Else if httpPath is a valid system file within server folder assigns systemPath to path to web_root+httpPath
            #EG: http://cs1.seattleu.edu:10540/foo/bar.jpg -> systemPath = home/st/pannud/p1b/web_root/foo/bar.jpg
            elif(os.path.isfile(sys.path[0] + '/web_root' + httpPath) == True):
                systemPath = sys.path[0] + '/web_root' + httpPath


            #If provided path is invalid returns 404 error and close connection
            #EG: http://cs1.seattleu.edu:10540/foo/bbhjklhb.jpg  
            elif(os.path.exists(sys.path[0] + '/web_root' + httpPath) == False):
                response = create_header(404)
                response += '\r\n\r\n'
                response = response.encode()
                conn.sendall(response)
                conn.close() 

            #If path  provided does exist, TRY
            if(os.path.exists(sys.path[0] + '/web_root' + httpPath) == True):
                try:   
                    #Open file at provided path
                    file_handler = open(systemPath,'rb')
                    #Read in contents of file
                    body = file_handler.read()
                    #obtain filetype
                    fileType = mimetypes.guess_type(systemPath)[0]
                    #obtain filesize
                    fileSize = os.path.getsize(systemPath)
                    #obtain timestamp in seconds
                    timeStamp = os.path.getmtime(systemPath)
                    #Convert timestamp into datetime format
                    lastModified = (datetime.fromtimestamp(timeStamp).strftime('%a, %d %b %Y %H:%M:%S %Z'))
                    #Create 200 OK header, encode and append file as body
                    response = create_header(200)
                    response += 'Content-Type: ' + fileType +'\r\n'
                    response += 'Content-Length: ' + str(fileSize) +'\r\n'
                    response += 'Last-Modified: ' + str(lastModified) + '\r\n\r\n'
                    response = response.encode()
                    response += body
                    conn.sendall(response)
                    file_handler.close()
                    conn.close()
            
                #shouldn't reach here but if it does just additional failsafe to prevent server crash
                #and send 500 message.
                except Exception as e:
                    response = create_header(500)
                    response += '\r\n\r\n'
                    response = response.encode()
                    conn.sendall(response)
                    conn.close()
        else:
            conn.close()
    
    #close connection at end of loop
    conn.close()
    
#Close socket
sock.close()