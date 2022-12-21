from socket import *
import os
import re


BUFFER_SIZE = 4096

# Web proxy function; designates what the web-proxy does.
def webProxy():    
    # Setup for hosting server. 
    connectToServerName = ""
    connectToServerPort = ""
    serverPort = 12345 # Server port number.
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    print('[+] Proxy server is ready to receive...')
    fileName = ""
    while True:
        connectionSocket, addr = serverSocket.accept()
        fileName = connectionSocket.recv(1024).decode()
        break
    # Parsing the request from the browser.
    words = fileName.split(' ')
    fileName = words[1]
    result = re.sub(r"^\/(\w+\.)+\w+:\d{0,5}", "", fileName)
    # Separates the URL into the URL to connect to, and the port number to connect on.
    connectToServerName = re.sub(r":.*", "", fileName)
    connectToServerName = re.sub(r"/", "", connectToServerName)
    connectToServerPort = re.sub(r"^\/(\w+\.)+\w+:", "", fileName)
    connectToServerPort = re.sub(r"/.*", "", connectToServerPort)
    print(f"[+] Client has sent {result} to the proxy...")

    fileFoundOnFirstPass = True
    done = False
    while not done:
        # Looking for file within local proxy folder (aka the current working directory).
        fileBool = False
        for dirpath, dirnames, filenames in os.walk(os.getcwd()): 
            for filename in filenames:
                if (filename == os.path.basename(result)): 
                    fileBool = True
    
        # If the file was found, open and send contents to client.
        if(fileBool == True):
            if(fileFoundOnFirstPass == True):
                print(f"[+] File was found on proxy. Sending file...")
            fileName = os.path.basename(fileName)
            with open(fileName, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    connectionSocket.sendall(bytes_read)
            print(f"[+] Sent {fileName} successfully...")
            connectionSocket.close()
            serverSocket.close()
            done = True
        # If file was not found, connect to webserver and download file.    
        if(fileBool == False):
            fileFoundOnFirstPass = False
            print(f"[-] File was not found on proxy, connecting to server...")
            serverName = connectToServerName # Web server used.
            serverPort = int(connectToServerPort) # Port for server.
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName, serverPort))
        
            # Set up the HTML request needed to get the file from the server.
            htmlRequest = f"GET http:/{fileName} HTTP/1.0\r\n\r\n"
            fileName = os.path.basename(fileName)
            clientSocket.send(htmlRequest.encode())
            with open(fileName, "wb") as f:
                while True:
                    bytes_read = clientSocket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
            print(f"[+] {fileName} is now on the proxy server.")
            clientSocket.close()
            serverSocket.close()

# Calls the web-proxy function as soon as the program runs; no need for command line parameters or anything of the like.
webProxy()
