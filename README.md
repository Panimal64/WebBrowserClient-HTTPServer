Web Client:
The purpose of this program is to send a GET request to a HTTP server
Obtain the HTTP Response, parse the response header from the body, and 
print out the body.

USE: Program can be executed by using the following command
python3 http_cli.py http://flask.pocoo.org 
to redirect the output to shell enter in format of following examples
python3 http_cli.py http://www.fortune.com >filename.txt
python3 http_cli.py http://flask.pocoo.org/static/logo/flask.png >filename.png

Web Server:
The purpose of this program is to run a basic web server that can respond to GET 
requests from http_cli.py, PostMan, or a web browser.
It will than determine if the GET request is valid, if so will return the page 
at the provided path with a response of 200 OK.  
If the request is anything other than a GET it will return error code 501.  
If the URL provided does not correspond to a file path on 
server it will respond with 404.  If the URL contains a bad request containing /../ 
it will respond with 400 and if there is a server 
error it will respond with 500 to prevent unauthorized file access

USE: python3 http_svr.py [PORT RANGE]


Note:  When using a web browser the server may output two responses  respond twice, the first is the actual
request/response and the second will be a 404 Not Found.  This is due to favicon implementation on web browsers
They send 2 requests, the first is the URL GET request, the second request is for  favicon.ico.  Since this servers 
web_root currently does not contain a favicon.ico that is why a 200 OK will be followed a 404.
