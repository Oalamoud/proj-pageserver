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


def fileHandler(filename):
    """
    Opens the requested file and returns the contant of the file if it is in html

    Takes:
        filename: The name of the file from the GET request
    Returns:
        The content of the file, if every thing work fine
        

    """
    # Handling the "../" and "./" in the get request
    if "./"in filename or  "../" in filename:
        return "HTTP/1.0 403 FORBIDDEN"
    filename= filename[1:] # get rid of the first character '/'
    

    if os.path.isfile(filename):   # if file in folder
        if filename.endswith(".html"): # if file is html
            #open the file
            f =open(filename,"r") 
            #return file content
            read_data= f.read()
            f.close()
            return read_data
            # return file content
                
        else:
            #Not found
            return "HTTP/1.0 403 FORBIDDEN\n\n"
    else:
        # This server soes not handle this type of files
        return "HTTP/1.0 404 NOT FOUND\n\n"



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
        transmit("HTTP/1.0 200 OK\n\n", sock)
        transmit(fileHandler(parts[1]), sock)
        #transmit(parts[1],sock)
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
    
