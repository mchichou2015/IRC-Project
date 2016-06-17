# IRC-Project
Socket Internet Relay Chat Class Project

This document describes a project to implement an IRC protocol allowing users to communicate with each other. In this system, we will have a central server that “relays” messages coming from a connected user to another connected user. 

Users can join/create rooms where they can exchange messages with 1 to many users.
Using the socket class and libraries of Python2.7, communication between server and clients will be conducted over TCP/IP socket connection. 

To run the server: python Med_IRC_SERVER.py

To run the client: Med_IRC_CLIENT

For simplicity the server and client will use the gethostname function, therefore
Client and server both must be run from same localhost but you can always specify your own 
hostname.


This IRC will not work on windows because i am using the python select function
to read data from both the socket and the input stream and this only works on linux.
