"""
Socket programming in Python
  as an illustration of the basic mechanisms of a web server.

  Based largely on https://docs.python.org/3.4/howto/sockets.html
  This trivial implementation is not robust:  We have omitted decent
  error handling and many other things to keep the illustration as simple
  as possible. 

  FIXED BY: Omar Alamoudi
"""

import socket    # Basic TCP/IP communication on the internet
import random    # To pick a port at random, giving us some chance to pick a port not in use
import _thread   # Response computation runs concurrently with main program 
import os        # Finding the file in the OS

def listen(portnum):
    """
    Create and listen to a server socket.
    Args:
       portnum: Integer in range 1024-65535; temporary use ports
           should be in range 49152-65535.
    Returns:
       A server socket, unless connection fails (e.g., because
       the port is already in use).
    """
    # Internet, streaming socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to port and make accessible from anywhere that has our IP address
    serversocket.bind(('', portnum))
    serversocket.listen(1)    # A real server would have multiple listeners
    return serversocket

def serve(sock, func):
    """
    Respond to connections on sock.
    Args:
       sock:  A server socket, already listening on some port.
       func:  a function that takes a client socket and does something with it
    Returns: nothing
    Effects:
        For each connection, func is called on a client socket connected
        to the connected client, running concurrently in its own thread.
    """
    while True:
        print("Attempting to accept a connection on {}".format(sock))
        (clientsocket, address) = sock.accept()
        _thread.start_new_thread(func, (clientsocket,))




def error(errorCode, msg='I dont handle this request, '):
    """
    Handle HTTP error codes

    args:
        errorCode: int it takes range of http codes (400,403,404) 
        msg:
            It takes a massage that you want to attach to the error
            Defualt massage "I don't handle this request, "
    
    returns:
        str: The massage followed by the error full code 
    """
    #list of possible error codes
    errors = {404:"404 NOT FOUND.\n",403:"403 FORBIDDEN.\n",400:"400 Bad Request.\n"}
    errorMsg = msg + errors[errorCode]   # genarate the error massage(msg)
    print(errorMsg) # Show the error on the console

    return errorMsg




def fileHandler(filename):
    """
    Opens the requested file and returns the contant of the file if it is in html or css

    args:
        filename: The name of the file from the GET request.
    
    Returns:
        str:
            File content:
                 HTML or CSS files, if every thing work fine.
           or
           error:
                400 bad request: if url contains any of the following("//","..","~")
                403 forbidden: if the requested file was not html or css
                404 not found: if the file was not found 

    """
    # Handling the "../" and "./" in the get request
    if "~"in filename or  ".." in filename or "//" in filename:
        return error(400)                           # http code 400 Bad request 
    filename= filename[1:]                          # remove the first character '/'
    if os.path.isfile(filename):                    # if file do exist in folder
        if filename.endswith(".html") or filename.endswith(".css"): # if file is html or css
            try:                                    # Try to opent the file
                f =open(filename,"r")               # Open the file
                read_data= f.read()                 # Read file content
                f.close()                           # Close the file
                return read_data
            except IOError:                     # Handling the error if cannot open/read file
                return error(404)               # http code 404  not found
        else:                                   # else file is neither .html nor .css
            return error(403)                   # http code 403 forbidden
    else:                                       # else file does not exist in folder
        return error(404)                       # http code 404 not found



def respond(sock):
    """
    Respond (only) to GET

    """
    sent = 0
    request = sock.recv(1024)  # We accept only short requests
    request = str(request, encoding='utf-8', errors='strict')
    print("\nRequest was {}\n".format(request))

    parts = request.split()
    if len(parts) > 1 and parts[0] == "GET":
        transmit("HTTP/1.0 200 OK\n\n", sock)  # send the header of the http request
        transmit(fileHandler(parts[1]), sock)  # Send the page content
        
    else:
        transmit("\nI don't handle this request: {}\n".format(request), sock)

    sock.close()

    return

def transmit(msg, sock):
    """It might take several sends to get the whole buffer out"""
    sent = 0
    while sent < len(msg):
        buff = bytes( msg[sent: ], encoding="utf-8")
        sent += sock.send( buff )
    

def main():
    port = random.randint(5000,8000)
    sock = listen(port)
    print("Listening on port {}".format(port))
    print("Socket is {}".format(sock))
    serve(sock, respond)

main()
    
