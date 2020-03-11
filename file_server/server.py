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
from threading  import Thread, Lock;
import time;
import os;
import signal;
import io;
from events         import BaseObject , Event, EventHandler;
from constants      import *;
from clientmanager  import ClientManager;
from client         import Client;
from request        import Request;


    
class DaemonServer(object):
    
    def __init__(self, **kwargs):
        self.__Port  = kwargs['port'] if(('port' in kwargs) and (type(kwargs['port']) == int)) else DEFAULT_PORT_ADDRESS;
        self.__StartLocker  =  Lock();
        self.__RunThread    = None;
        self.__IsRunning    = False;
        self.__Socket       = None;
        self.__HostAddress  = None;
        self.__BackLogConnections =  DEFAULT_BACK_LOG_CONNECTION ;
        self.__Clients              = ClientManager();
        self.__ThreadPoles          = list();
        self.__ClientConnected      = EventHandler();
        self.__ClientDisconnected   = EventHandler();
        
    @property
    def ClientConnected(self):
        return self.__ClientConnected;

    @ClientConnected.setter
    def ClientConnected(self, handler):
        if(isinstance(handler , EventHandler)):
            self.__ClientConnected   =  handler;
    @property
    def ClientDisconnected(self):
        return self.__ClientDisconnected;

    @ClientDisconnected.setter
    def ClientDisconnected(self, handler):
        if(isinstance(handler , EventHandler)):
            self.__ClientDisconnected   =  handler;

    @property
    def BackLogConnections(self):
        return self.__BackLogConnections;
    
    @BackLogConnections.setter
    def BackLogConnections(self, value):
        if type(value) is not int:
            raise TypeError("@Backlog : expecting an integer value");
        self.__BackLogConnections = value;
        
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
                if(value is True) :
                    if self.__IsRunning is not True:
                        self.Start();
                else:
                    if self.__IsRunning:
                        if value is not True:
                            self.Stop(); 

    def __InBackground(self):
        self.__StartLocker.release();
        self.__IsRunning  = True;
        print("Server started at : {0}:{1}".format(self.HostAddress, self.Port));
        while(self.IsRunning):           
            while(self.__Socket != None):
                try:
                    self.__Socket.listen(self.BackLogConnections);
                    socket, address  = self.__Socket.accept();
                    
                    if(socket != None):
                        client  = Client(socket=socket , timeout=0)
                        newConnetionThread  =  Thread(target= self.__HandleNewConnection, args=(client, ));
                        newConnetionThread.daemon  = False;
                        newConnetionThread.start();
                        self.__ThreadPoles.append(newConnetionThread);
                except Exception as err:
                    print(err);
                    if(self.IsRunning):
                        self.Stop();
                    raise err;
                finally:
                    #Remove all client and send and if possible send them
                    # A server shutdow message
                    pass;
        self.Stop();

    def __HandleNewConnection(self, client):
        try:
            if(client != None):
                self.Clients.Add(client);
                while(True):
                    message  = client.Read();
                    if not message :
                        client.Close();
                        break;
                    else:
                        request  =  Request.Parse(message);
                        print(request);
        except Exception as err:
            print(err);
            print(client);
            pass;
  

    def Stop(self):
        self.__StartLocker.acquire();
        try:
            if(self.IsRunning):
                self.__IsRunning  = False;
                if(self.__RunThread.is_alive()):
                    self.__RunThread.join(WAIT_THREAD_INTERVAL);
                if(self.__Socket != None):
                   self.__CloseAllClient();
                   self.__Socket.close();
               
        except Exception as err:
            print(err);
        finally:
            self.__RunThread  = None;
        self.__StartLocker.release();


    def __CloseAllClient(self):
       self.Clients.Clear();


    
if(__name__ =="__main__"):
    def run(port):
        server = DaemonServer(port = port);
        server.Start();
        try:
            while(server.IsRunning):
                
                pass;
        except Exception as err:
            print("Stop unexceptedly - {0}".format(err));
        finally:
            server.Stop();
        
    def start_server_at(port):
        t  =  Thread(target = run, args=(port,));
        t.start();
    start_server_at(8082);
    
    while(True):
       pass;
        

