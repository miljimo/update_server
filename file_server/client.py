import socket;
import uuid;
from threading import Thread, Lock;
from constants import *;
from events import BaseObject , Event, EventHandler;

class Client(object):

    def __init__(self, **kwargs):
        soc = kwargs['socket'] if('socket' in kwargs) else None
        self.__Socket        =  soc;
        self.__IsOpened      =  True if(isinstance(soc, socket.socket)) else False;
        self.__Closed        =  EventHandler();
        self.__ReadLock      =  Lock();
        self.__SessionUID    = uuid.uuid4();
        self.__Timeout       = kwargs['timeout'] if (('timeout' in kwargs) and ((type(kwargs['timeout'])== int) or (type(kwargs['timeout'])== float))) else 5;
        if(self.__IsOpened):
             self.__Socket.settimeout(self.__Timeout);
            
    def Open(self, host, port):
        self.__ReadLock.acquire();
        if(self.IsOpened is not True):
            self.__Socket  =  socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            self.__Socket.settimeout(self.__Timeout);
            try:
                timeout  =  self.__Socket.gettimeout();
                print("Default Time out {0}".format(timeout));
                self.__Socket.connect((host, port));
                self.__IsOpened = True; 
            except  Exception as err :
                print(err);
            finally:
                pass;
        self.__ReadLock.release();
        return self.IsOpened;
            

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


if(__name__ =="__main__"):
    client  =  Client(timeout  = 5.90);
    status  = client.Open("10.10.0.45", 8082);
    print("Started");
    while(status != True):
        print("Reconnecting: 1");
        status  = client.Open("10.10.0.45", 8081);
    print("Connection Status = {0}".format(status));
    data   = client.Read();
    print(data);
    client.Close();
    
    
