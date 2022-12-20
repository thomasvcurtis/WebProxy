from socket import *
import sys
import os


BUFFER_SIZE = 4096

# TODO: Create a loop to check whether or not the file has been sent to the client. Clean up code.
def webProxy():    
    # Setup for hosting server. 
    serverPort = 12345 # server number
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
    words2 = fileName.split('/')
    result = words2[2]
    words3 = fileName.split('/')
    print(words3)
    result = f"/{words3[2]}/{words3[3]}"
    print(result)
    print(f"[+] Client has sent {result} to the proxy...")

    # Looking for file within local proxy folder.
    fileBool = False
    for dirpath, dirnames, filenames in os.walk("/home/brywhit/proxy-server"): 
        for filename in filenames:
            print(filename)
            if (filename == os.path.basename(result)): 
                print(os.path.join(dirpath, filename))
                fileBool = True
    
    # If the file was found, open and send contents to client.
    if(fileBool == True):
        print(f"[+] File was found on proxy, no need to connect to server. Sending file...")
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
    # If file was not found, connect to webserver and download file.    
    if(fileBool == False):
        print(f"[-] File was not found on proxy, connecting to server...")
        serverName = "csvm07.cs.bgsu.edu" # Web server used.
        serverPort = 80 # Port for server.
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        htmlRequest = f"GET http:/{fileName} HTTP/1.0\r\n\r\n"
        print(htmlRequest)
        fileName = os.path.basename(fileName)
        clientSocket.send(htmlRequest.encode())
        with open(fileName, "wb") as f:
            while True:
                bytes_read = clientSocket.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
        print(f"[+] {fileName} is now on the proxy server. Retry to send to client.")
        clientSocket.close()
        serverSocket.close()
        # Call webProxy() again to loop?
        webProxy()


if (sys.argv[1] == '1'): # To call, use python3 task1-unix.py 1 <machine name>.
    webProxy()
