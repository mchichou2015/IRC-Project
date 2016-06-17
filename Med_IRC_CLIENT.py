import socket
import select
import sys

if __name__ == "__main__":
    #get in put from the user
    print "Welcome to My IRC client Application"
    print "Please enter the Server host name :"
    host =socket.gethostname()
    print "Please enter the Server port number :"
    port = 9999
    print "Please choose a nickname :"
    nickname = raw_input()
    print host , port,nickname
    # create a TCP socket and set a timeout
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to the server
    try:
        s.connect((host, port))
    except:
        print "Something went wrong.Unable to connect"
        sys.exit()
    #send the nickname to the server to see if it is not already used
    try:
        s.send(nickname)
    except:
        print "Something went wrong.Unable to connect"
        sys.exit()


    while True:
        socket_list = [sys.stdin, s]
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for socket in read_sockets:

            # if the socket is received from server then we can read the message
            if socket == s:
                try:
                    msg = s.recv(1024)
                    if msg.split(':')[0] == "send":
                        filename = msg.split(':')[1]
                        f = open(filename, 'rb')
                        l = f.read(1024)
                        while l:
                            s.send(l)
                            print('Sending data...')
                            l = f.read(1024)
                        f.close()
                        s.send("End_0F_File")
                    elif msg.split(':')[0] == "receive":
                        filename = msg.split(':')[1]
                        with open(filename, 'wb') as f:
                            print 'file opened'
                            while True:
                                print('receiving data...')
                                msg = s.recv(1024)
                                if msg.endswith("End_0F_File"):
                                    f.write(msg[:-11])
                                    break
                                f.write(msg)

                            f.close()
                        print('Successfully got the file')
                    else :
                        if msg:
                            print msg
                except:
                    print "Something went wrong.Unable to connect"
                    sys.exit()
                # done receiving , now we can send
            else:
                msg = raw_input()
                try:
                    if msg :
                        s.send(msg)
                except:
                    print "Something went wrong.Unable to connect"
                    sys.exit()