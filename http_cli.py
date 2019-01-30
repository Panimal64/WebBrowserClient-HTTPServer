""" Dave Pannu
CPSC 5510 P1a
The purpose of this program is to send a GET request to a HTTP server
Obtain the HTTP Response, parse the response header from the body, and 
print out the body.
USE: Program can be executed by using the following command
python3 http_cli.py http://flask.pocoo.org 
to redirect the output to shell enter in format of following examples
python3 http_cli.py http://www.fortune.com >filename.txt
python3 http_cli.py http://flask.pocoo.org/static/logo/flask.png >filename.png  """

import socket
import sys
import select
import os

HOST = ''   #Empty Host address
PATH = '/'  #Default Path
PORT = '80' #Default Port
sock = None


#Verify that URL was included as command line arguement
try:
    argString = sys.argv[1]
except IndexError:
    sys.stderr.write("No Command Line Arguement Provided, Exiting\n")
    sys.exit(1)


#Parse URL into Segments 
Segments = argString.split('/')


#Delete 'HTTP:' & '/' from Segment list of Parsed URL
if(Segments[0].find('http:') != -1):
    del Segments[0:2]


#If URL contained PATH extracts from Segments and sets PATH to it
if (len(Segments) >= 2):
    PATH += '/'.join(Segments[1:]) 


#If URL contains PORT number extracts it from HOST and sets PORT to it
if(Segments[0].find(':') != -1):
    #Split URL at :
    temp = Segments[0].split(':')
    #Insert URL without PORT into Segments[0]
    Segments.insert(0, temp[0])
    #Insert PORT into Segments[1]
    Segments.insert(1, temp[1])
    #Delete URL with PORT from SEGMENTS
    Segments.pop(2)
    #Set PORT to Segments[1] which contains PORT number
    PORT = Segments[1]
    #If Port is empty exit program
    if not PORT:
        sys.stderr.write("No PORT number provided after ':', Exiting Program\n")
        sys.exit(1)


#Sets HOST to url
HOST = Segments[0]

#DEBUG
#request = b"GET / HTTP/1.1\r\nHost:flask.pocoo.org\r\nConnection: close\r\n\r\n"
#print(request)

#Piece together GET message using PATH and HOST and Prints to STD error
message = 'GET ' + PATH +' HTTP/1.1\r\n'
message +='Host:' + HOST + '\r\n' 
message +='Connection: close\r\n\r\n'
sys.stderr.write(message)


#Encode message to utf-8 
request = message.encode()


#Create socket using passed in HOST and PORT information
try:
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            sock = socket.socket(af, socktype, proto)
        except OSError as msg:
            sock = None
            continue
        try:
            sock.connect(sa)
        except OSError as msg:
            sock.close()
            sock = None
            continue
        break
    if sock is None:
        sys.stderr.write('Unable to open socket\n')
        sys.exit(1)
except OSError:
    sys.stderr.write("Malformed URL, exiting program\n")
    sys.exit(1)


#Send request to server
try: 
    sock.sendall(request)
except OSError:
    sys.stderr.write("Error sending request, exiting program\n")
    sys.exit(1)

#Set empty result to recieve binary data
binaryHeader = b''


#While loop to recieve binary header until \r\n\r\n from socket
endOfHeader = b'\r\n\r\n'
try:
    while endOfHeader not in binaryHeader:
        pieces = sock.recv(1)
        if not pieces: break
        binaryHeader += pieces
except OSError:
    sys.stderr.write("Error recieving from socket, exiting program\n")
    sys.exit(1)



#Parse out header from recieved data ***REMOVED FOR REVISION (DEADCODE) LEFT AS A REFERENCE TO WHAT WAS PREVIUSLY DONE***
"""binaryHeader = result.split(b'\r\n\r\n')[0]"""


#Decode binary header into String for cleaner printing
header = binaryHeader.decode()


#Print Header to stderr
sys.stderr.write(header)


#Set empty body for binary data
body = b''

#If header contained Content-Length.  
#Parse content-length from header and join list to int 
#Then recieve content from socket until amount recieved matches contentlength provided
#Else just print out body, since some sites like www.google.com do not provide content length
if 'Content-Length: ' in header:
    start = 'Content-Length: '
    end = '\r\n'
    contentLength = (header.split(start))[1].split(end)[0]
    contentLengthInt = int(''.join(str(i) for i in contentLength))
    bytesLeft = contentLengthInt
    try:
        while bytesLeft > 0:
            data = sock.recv(256)
            if not data: break
            bytesLeft -= len(data)
            body += data
    except OSError:
        sys.stderr.write("Error recieving from socket, exiting program\n")
        sys.exit(1) 
    #Obtain body of message from result ***REMOVED FOR REVISION (DEADCODE) LEFT AS A REFERENCE TO WHAT WAS PREVIOUSLY DONE***
    """body = result[len(header)+4:]"""
    #DEBUG
    """print(len(result))
    print(len(header))
    print(len(body))
    print(contentLengthInt)
    """
    #Verify that length of body matches contentlengthint ***SHOULD BE DEAD CODE NOW BUT LEFT JUST INCASE***
    if(len(body) != contentLengthInt):
        sys.stderr.write("Size of body did not match content-length from server. Exiting\n")
        sys.exit(1)
    #Print body to stdout 
    sys.stdout.buffer.write(body)
else:
    try:
        while True:
            pieces = sock.recv(256)
            if not pieces: break
            body += pieces
        sys.stdout.buffer.write(body)
    except OSError:
        sys.stderr.write("Error recieving from socket, exiting program\n")
        sys.exit(1)

#Close Socket
sock.close()
