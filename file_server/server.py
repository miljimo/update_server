"""
 Using the comsumer and producer pattern
 to implement a file update server
 that will monitor which file is updated and serve
 it the client application.
 The is a continues live connection
 communication this allow the server
 to send update asynchrously to and from the client and the server
"""

import socket;
from threading import Thread, Lock;
import time;
import os;
import signal; # Handle system signals
from events import BaseObject , EventHandler;
from filewatchers import FileWatcher;

DEFAULT_PORT_ADDRESS  = 36061;

class SignalHandler(object):
    def __init__(self):
        super().__init__();



class DaemonServer(object):

    __CLASS__     = None;
    __INSTANCE__  = None;

    #Implemeny single pattern in Python.
    def __new__(cls, *args, **kwargs):
        if(cls != None):
            # There is class for this Server
            # if this server have same address information
            cls.__CLASS__  =  cls;
            cls.__INSTANCE__  =  super().__new__(cls);
        return cls.__INSTANCE__;
        

    
    def __init__(self, **kwargs):
        self.__Port  = kwargs['port'] if(('port' in kwargs) and (type(kwargs['port']) == int)) else DEFAULT_PORT_ADDRESS;
        self.__StartLocker  =  Lock();
        self.__RunThread    = None;
        self.__IsRunning    = False;
        self.__CanStart     = False;
        self.__Socket       = None;
        self.__HostAddress  = None;
        self.__Clients      = list();
        self.ThreadPoles    = list();
        
    @property
    def Clients(self):
        return self.__Clients;
        
    @property
    def HostAddress(self):
        return self.__HostAddress;
    
    @HostAddress.setter
    def HostAddress(self, hostaddress):
        if(type(hostaddress) != str):
            raise ValueError("@Invalid hostaddress provided");
        if(self.IsRunning):
            print("Unable to set the host address while server is running");
            return ;
        else:
            self.__HostAddress = hostaddress;
    
    @property
    def Port(self):
        return self.__Port;

    @Port.setter
    def Port(self, value):
        if(self.IsRunning == True):
            print("Unable to change port when server is running");
            # Throw a message to the users;
            return ;
        if(type(value) != int):
            raise TypeError("@Port: expecting an integer value");
        self.__Port = value;

    def Start(self):
        self.__StartLocker.acquire();
        if(self.IsRunning == True):
            print("Unable to start server when server is already started");
            return ;
        if(self.__Socket == None):
            # Create TCP socket
            self.__Socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            if(self.HostAddress == None):
                self.HostAddress  = socket.gethostbyname(socket.gethostname());
            self.__Socket.bind((self.HostAddress, self.Port));
            self.__Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__RunThread = Thread(target  = self.__InBackground);
            self.__RunThread.daemon  = True;
            self.__RunThread.start();
        
    @property
    def IsRunning(self):
        return self.__IsRunning;

    @IsRunning.setter
    def IsRunning(self, value):
        if(type(value) == bool):
            if(value != self.__IsRunning):
                if( (value  == True) and (self.__CanStart == True)):
                    # I think user want to start the server by setting this property to true;
                    # The server is not running and this
                    self.Start();
                else:
                    if(self.__IsRunning):
                        # The server is running
                        if(value == True):
                            print("Unable to start server when server is already running");
                        else:
                            self.Stop(); # stop the server
                            
            self.__IsRunning  = value;
                    

    def __InBackground(self):

        self.__StartLocker.release();
        self.__IsRunning  = True;
        self.__CanStart   = False;
        print("Server started at : {0}:{1}".format(self.HostAddress, self.Port));
        while(self.IsRunning and (self.__Socket != None)):
            try:
                print("Waiting for connections: ");
                self.__Socket.listen(5);
                client, address  = self.__Socket.accept(); 

                print(client, address);
                print("**********************")
                self.Clients.append(client);
                name =  client.getpeername();
                print("Number of Connections = {0}".format(name));
               
                newConnetionThread  =  Thread(target= self.OnNewConnection, args=(address, client));
                newConnetionThread.daemon  = False;
                newConnetionThread.start();
                self.ThreadPoles.append(newConnetionThread);
            except Exception as err:
                # Raise error events and terminate the server;
                if(self.IsRunning):
                    self.Stop();
                print(err);
            finally:
                #Remove all client and send and if possible send them
                # A server shutdow message
                print("Finally");
                pass;

    def OnNewConnection(self, address, client):
        print("New Connection Started");
        if(client != None):
            while(True):
                data  =   client.recv(4096);
                print(data);

    def Stop(self):
        self.__StartLocker.acquire();
        try:
            if(self.IsRunning):
                self.__IsRunning  = False;
                if(self.__RunThread.isAlive()):
                    self.__RunThread.join(1);
                if(self.__Socket != None):
                    # Close all client connections;
                    for client in self.Clients:
                        client.close();
                    self.__Socket.close();
               
        except Exception as err:
            print(err);
        finally:
            self.__RunThread  = None;
            self.__CanStart   = True;
        self.__StartLocker.release();

    



if(__name__ =="__main__"):
    server = DaemonServer();
    server.Start();
    try:
        while(server.IsRunning):
            pass;
        server.Stop();
    except Exception as err:
        print("Stop unexceptedly - {0}".format(err));
    finally:
        server.Stop();
        

