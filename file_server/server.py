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
from events import BaseObject , Event, EventHandler;


DEFAULT_PORT_ADDRESS        = 36061;
DEFAULT_BACK_LOG_CONNECTION = 5;
DEFAULT_READ_BLOCK          = 4096;
WAIT_THREAD_INTERVAL        = 1.05;

class SignalHandler(object):
    def __init__(self):
        super().__init__();

class Parser(object):

    def Parse(self, data:bytearray):
        if(type(data) != bytearray):
            raise TypeError("@Expecting a data array");

            
class Request(object):

    def __init__(self, raw_bytes):
        self.__RawBytes  = raw_bytes;
        if(len(self.__RawBytes) <= 0) and (type(self.__RawBytes) != bytearray):
            raise TypeError("@Request Expecting a byte array");

        self.__Header  =  None;
        self.__Content =  None;

    @property
    def RawData(self):
        return  self.__RawBytes;

"""
  Version           : 2bytes
  Packat-Id         : 2bytes
  Session-Length    : 1bytes;
  Session-UID       : 
  Offset            : 2bytes;
  
  
"""
class Header(object):

    def __init__(self):
        self.__Version     = 0x00;
        self.ContentLength = 0x0000;
        pass;

class Content(object):

    def __init__(self, data: bytearray):
        self.__Length  =  len(data);
        self.__Data    =  data;
        pass;


class Client(object):

    def __init__(self, soc):
        if(isinstance(soc, socket.socket)) is not True:
            raise TypeError("Expecting a socket type");
        self.__Socket        =  soc;
        self.__IsOpened      =  True;
        self.__Closed  =  EventHandler();
        self.__ReadLock  =  Lock();

    @property
    def Port(self):
        return self.__Socket.getpeername()[1];
    
    @property
    def IpAddress(self):
        return self.__Socket.getpeername()[0];

    @property
    def Closed(self):
        return self.__Closed

    @Closed.setter
    def Closed(self, handler):
        if(isinstance(handler,EventHandler)):
           if(self.__Closed == handler):
               self.__Closed = handler;        

    def Write(self , data:bytearray):
        self.__ReadLock.acquire();
        result =  0;
        if(self.IsOpened):
            result  = self.__Socket.send(data);
        self.__ReadLock.release();
        return result;

    def Read(self , nSize = DEFAULT_READ_BLOCK ):
        self.__ReadLock.acquire();
        result =  None;
        if(self.IsOpened)  and (type(nSize) is int):
            data_recieved =  self.__Socket.recv(nSize);
            if(len(data_recieved) > 0):
                result = data_recieved;
        self.__ReadLock.release();
        return result;
        
    @property
    def IsOpened(self):
        return self.__IsOpened;

    def Close(self):
        self.__ReadLock.acquire();
        if(self.__IsOpened is True):
            self.__IsOpened  =  False;
            self.__Socket.close();
            if(self.Closed is not None):
                self.Closed(Event("socket.event.close"));
        self.__ReadLock.release();



            

class ClientManager(object):

    def __init__(self):
        self.__Clients  =  dict();
        self.__Locker  =  Lock();
        pass;
    
    def Add(self, client):
        self.__Locker.acquire();
        status  = False;
        ipaddress  =  "{0}:{1}".format(client.IpAddress, client.Port);
        if(ipaddress not in self.__Clients):
            self.__Clients[ipaddress] = client;
            status  =  True;
        self.__Locker.release();
        return status;

    def Delete(self, client):
        self.__Locker.acquire();
        status  =  False;
        ipaddress  =  "{0}:{1}".format(client.IpAddress, client.Port);
        if(ipaddress in self.__Clients):
            del self.__Clients[ipaddress];
            status  =  False;
        self.__Locker.release();
        return status;

    def Clear(self):
        self.__Locker.acquire();
        for ipaddress in self.__Clients:
            client =  self.__Clients[ipaddress];
            client.Close();
            del self.__Clients[ipaddress];            
        self.__Locker.release();
        
    
    @property
    def Count(self):
        return len(self.__Clients);
    
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
        
        while(self.IsRunning and (self.__Socket != None)):
            try:
                self.__Socket.listen(self.BackLogConnections);
                socket, address  = self.__Socket.accept();
                client  = Client(socket)
                newConnetionThread  =  Thread(target= self.OnNewConnection, args=(client, ));
                newConnetionThread.daemon  = False;
                newConnetionThread.start();
                self.__ThreadPoles.append(newConnetionThread);
                print("IpAddress = {0}, Port = {1}/n".format(client.IpAddress,client.Port ));
            except Exception as err:
                if(self.IsRunning):
                    self.Stop();
                raise err;
            finally:
                #Remove all client and send and if possible send them
                # A server shutdow message
                pass;

    def OnNewConnection(self, client):
        if(client != None):
            self.Clients.Add(client);
            while(True):
                data  =   client.Read();
                client.Write("HTTP/1.1 200 OK");
                if not data:
                    client.Close();
                    break;
                print(data);
                
  

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

def run(port):
    server = DaemonServer(port = port);
    server.Start();
    try:
        while(server.IsRunning):
            pass;
        server.Stop();
    except Exception as err:
        print("Stop unexceptedly - {0}".format(err));
    finally:
        server.Stop();
        
def start_server_at(port):
    t  =  Thread(target = run, args=(port,));
    t.start();
    
if(__name__ =="__main__"):
   start_server_at(8081);
   start_server_at(8082);
   start_server_at(8083);
   while(True):
       pass;
        

