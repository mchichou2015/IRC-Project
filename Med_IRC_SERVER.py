import socket
import select
import sys

# function that print the menu to the appropriate socket
def menu(sock):
    sock.send("          Welcome to Med-IRC           \n")
    sock.send("              Main Menu                    \n")
    sock.send("Please choose from the following options :\n")
    sock.send("/create-------------------------create a room\n")
    sock.send("/rooms--------------------------List all rooms\n")
    sock.send("/join---------------------------join a room\n")
    sock.send("/leave--------------------------leave a room\n")
    sock.send("/list---------------------------list members of a room\n")
    sock.send("/msg:nickname:your message------Send a private nessage\n")
    sock.send("/send:nickname:filename---------Send a file\n")
    sock.send("/q------------------------------Disconnect from the Server\n")


if __name__ == "__main__" :
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096
    PORT = 9999
    HOST = socket.gethostname()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    # List to keep track of nicknames
    NICKNAMES_LIST = []
    # List to keep track of rooms
    ROOMS_LIST =[]
    # dictionary to store info about each client socket
    client ={}
    prv_msg = False
    # room variable
    room = "none"

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    print "Chat server started on port %s"%PORT
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

        for sock in read_sockets:
            # New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr

                nickname = sockfd.recv(RECV_BUFFER)
                # receive the nickname and check if it is taken
                if nickname in NICKNAMES_LIST:
                    sockfd.send("Sorry, this nickname is already taken ! Please try again:")
                    sockfd.close()
                    CONNECTION_LIST.remove(sockfd)
                else:
                    # nickname is free ,we can add it to our list and proceed.
                    NICKNAMES_LIST.append(nickname)
                    # store info about the current client in the dictionary
                    client[sockfd] = {'nickname': nickname, 'current_room': '', 'joined_rooms': [],'prv_msg': ''}
                    # show the menu to the client
                    sockfd.send("Welcome %s .You are now connected !\n" % nickname)
                    menu(sockfd)
            # Some incoming message from a client
            else:
                try:
                    # we start by receiving a message from a client
                    msg = sock.recv(RECV_BUFFER)
                    # option to create a room
                    if msg == "/create":
                        sock.send("Please enter the name of the room you want to create:\n")
                        room = sock.recv(RECV_BUFFER)
                        if room in ROOMS_LIST:
                            sock.send("Sorry, this room already exisit !\n")
                        else:
                            # nickname is free ,we can add it to our list and proceed.
                            ROOMS_LIST.append(room)
                            sock.send("Room #%s is successfully created!\n\n\n"%room)
                        sock.send("/0 to for main menu !!\n")

                    # option to list all rooms
                    if msg == "/rooms":
                        if not ROOMS_LIST:
                            sock.send("Sorry,no rooms to list !\n")
                        else:
                            sock.send("This is the list of all available rooms:\n")
                            for room in ROOMS_LIST:
                                sock.send("#%s:\n"%room)
                        sock.send("/0 to for main menu !!\n")
                    # option to join a room
                    if msg == "/join":
                        sock.send("Please enter the name of the room you want to join:\n")
                        sock.send("You don't need to enter the # !\n")
                        room = sock.recv(RECV_BUFFER)
                        if room in ROOMS_LIST:
                            sock.send("You are now in room :#%s\n"%room)
                            sock.send("You can start sending messages :\n")
                            sock.send("/0 to for main menu !!\n")
                            client[sock]['joined_rooms'].append(room)
                            client[sock]['current_room'] = room
                        # room that you want to join is not in the list.
                        else:
                            sock.send("Sorry,The room you want to join does not exist!\n")
                            sock.send("/0 to for main menu !!\n")
                    # option to leave a room
                    if msg == "/leave":
                        sock.send("Please enter the name of the room you want to leave:\n")
                        sock.send("You don't need to enter the # !\n")
                        room = sock.recv(RECV_BUFFER)
                        if room in client[sock]['joined_rooms']:
                            sock.send("You successfully left  :#%s\n\n\n" % room)
                            client[sock]['current_room'] = ''
                            client[sock]['joined_rooms'].remove(room)
                        else:
                            # room that you want to join is not in the list.
                            sock.send("Sorry,you must be in a room before you can leave it!\n")
                        sock.send("/0 to for main menu !!\n")
                    # option to list members of  a room
                    if msg == "/list":
                        noMembers = False  # we use this in case of no members in list
                        sock.send("Please enter the name of the room you want to list it's members:\n")
                        sock.send("You don't need to enter the # !\n")
                        room = sock.recv(RECV_BUFFER)
                        if room in ROOMS_LIST:
                            sock.send("This is a list of all members of room: #%s\n" % room)
                            for c in client:
                                if room in client[c]['joined_rooms']:
                                    sock.send("%s\n" % client[c]['nickname'])
                                    noMembers = True
                            if not noMembers:
                                sock.send("!!No one is in this Room\n")
                        else:
                            # room that you want to join is not in the list.
                            sock.send("Sorry,no room of this name exist!\n")
                        sock.send("/0 to for main menu !!\n")
                    # option to send private message to a  member
                    if msg.split(':')[0] == "/msg":
                        member = msg.split(':')[1]
                        if member in NICKNAMES_LIST:
                            for s in CONNECTION_LIST:
                                if s != server_socket and s != sock:
                                    if client[s]['nickname'] == member :
                                        s.send(member+"-->"+msg.split(':')[2])
                                        sock.send("Sent !\n")

                        else:
                            sock.send("\n!!No one has this nickname\n")
                        sock.send("/0 to for main menu !!\n")
                    # option to show the main menu
                    if msg == "/0":
                        menu(sock)
                    # option to send a file
                    if msg.split(':')[0] == "/send":
                        member = msg.split(':')[1]
                        filename = msg.split(':')[2]
                        # server receive file from sender
                        sock.send("send:"+filename)
                        with open(filename, 'wb') as f:
                            print 'file opened'
                            while True:
                                print('receiving data...')
                                data = sock.recv(1024)
                                if data.endswith("End_0F_File"):
                                    f.write(data[:-11])
                                    break
                                f.write(data)
                            f.close()
                        print('Successfully received the file')
                        # now server can send it to the user
                        sock.send("send:"+filename)
                        if member in NICKNAMES_LIST:
                            for s in CONNECTION_LIST:
                                if s != server_socket and s != sock:
                                    if client[s]['nickname'] == member:
                                        s.send("receive:"+filename)

                                        #s.sendall("Begining_0f_file")
                                        f = open(filename, 'rb')
                                        l = f.read(1024)
                                        while l:
                                            s.send(l)
                                            print('Sending data...')
                                            l = f.read(1024)
                                        f.close()
                                        s.send("End_0F_File")
                                        print('Successfully delivered the file')
                        else :
                            sock.send("Sorry the receivers name cannot be found!\n")

                    if msg == "/q":
                        sock.send("Thank you and Goodbye !\n")
                        print "Client (%s, %s) is offline" % addr
                        # delete the socket from our dictionary
                        del client[sock]
                        # remove the socket from the list of active connections
                        CONNECTION_LIST.remove(sock)
                        # remove the nickname to make it available for others to use
                        NICKNAMES_LIST.remove(nickname)
                        sock.close()
                    if not msg.startswith("/"):
                        for s in CONNECTION_LIST:
                            if s != server_socket and s != sock:
                                # send messages to client sharing the same current room
                                if client[s]['current_room'] == client[sock]['current_room'] and \
                                                client[s]['current_room'] != '':
                                    s.send("#" + client[s]['current_room'] + "-->" + client[sock]['nickname'] +
                                           " : " + msg)



                except:
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    continue

    server_socket.close()








