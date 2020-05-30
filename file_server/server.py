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

class ISocketServer(object):

    def Start(self):
        raise NotImplementedError("@Start: method must be implemented");

    def Stop(self):
        raise NotImplementedError("@Stop: method must be implemented");


    @property
    def HostAddress(self):
        raise NotImplementedError("@HostAddress: property must be implemented");


class SocketCloseException(Exception):

    def __init__(self, inner_exception:Exception):
        if(isinstance(inner_exception , Exception) is not True):
            raise TypeError("Expecting an exception object as first parameter");        
        super().__init__('close_exception:');
        self.__InnerException = inner_exception;
        
    @property
    def InnerException(self):
        return self.__InnerException;

class SocketStartEvent(Event):

    def __init__(self, source : object):
        if(isinstance(source , ISocketServer) is not True):
            raise TypeError("SocketStartEvent: expecting a ISocketServer object");
        super().__init__('socket.start.event');
        self.__Source  =  source;

    @property
    def Socket(self):
        return self.__Source;
        
        
class SocketCloseEvent(Event):

    def __init__(self, exception: SocketCloseException):
        
        if(isinstance(exception, SocketCloseException) is not True):
            raise TypeError("@SocketCloseEvent: expecting an SocketCloseException object ");
        super().__init__("socket.close.event");
        self.__Exception = exception;

    @property
    def Exception(self):
        return self.__Exception;

class SocketAcceptedEvent(Event):

    def __init__(self, source :ISocketServer, client: socket.socket, ipaddress:str):
        if(isinstance(source,ISocketServer) is not True):
            raise TypeError("@SocketAcceptedEvent : expecting paremeter 2 to be a ISocketServer object");
        super().__init__("socket.accept.event");
        self.__Source    =  source;
        self.__Socket    =  client;
        self.__IpAddress =  ipaddress;

    @property
    def Socket(self):
        return self.__Socket;
    
    @property
    def IpAddress(self):
        return self.__IpAddress;

    @property
    def Source(self):
        return self.__Source;
        
        
    
class SocketServer(ISocketServer):
    
    def __init__(self, **kwargs):
        self.__Port  = kwargs['port'] if(('port' in kwargs) and (type(kwargs['port']) == int)) else DEFAULT_PORT_ADDRESS;
        self.__StartLocker  =  Lock();
        self.__RunThread    = None;
        self.__IsRunning    = False;
        self.__Socket       = None;
        self.__HostAddress  = None;
        self.__BackLogConnections   = DEFAULT_BACK_LOG_CONNECTION ;
        self.__Accepted             = EventHandler();
        self.__Closed               = EventHandler();
        self.__Started              = EventHandler();

    @property
    def Started(self):
        return self.__Started;

    @Started.setter
    def Started(self, handler):
        if(handler == self.__Started):
            self.__Started  =  handler;

    @property
    def Closed(self):
        return self.__Closed;

    @Closed.setter
    def Closed(self, handler):
        if(handler == self.__Closed):
            self.__Closed =  handler;
     
        
    @property
    def Accepted(self):
        return self.__Accepted;

    @Accepted.setter
    def Accepted(self, handler):
        if(isinstance(handler , EventHandler)):
            self.__Accepted   =  handler;

    @property
    def BackLogConnections(self):
        return self.__BackLogConnections;
    
    @BackLogConnections.setter
    def BackLogConnections(self, value):
        if type(value) is not int:
            raise TypeError("@Backlog : expecting an integer value");
        self.__BackLogConnections = value;
        
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
        # Tell the users that the socket has be started.
        if(self.Started != None):
            self.Started(SocketStartEvent(self));
         
        while(self.IsRunning):           
            if(self.__Socket != None):
                try:
                    self.__Socket.listen(self.BackLogConnections);
                    socket, address  = self.__Socket.accept();
                    if(socket != None):
                        if(self.Accepted != None):
                            self.Accepted(SocketAcceptedEvent(self, socket, address));                       
                        pass;
                      
                except Exception as err:
                    self.Stop();
                    if(self.Closed != None):
                        self.Closed(SocketCloseEvent(SocketCloseException(err)));                    
                finally:
                    pass;
        self.Stop();

   

    def Stop(self):
        self.__StartLocker.acquire();
        try:
            if(self.IsRunning):
                if(self.__RunThread.is_alive()):
                    self.__IsRunning  = False;
                    self.__RunThread.join(WAIT_THREAD_INTERVAL);
                if(self.__Socket != None):                   
                   self.__Socket.close();
               
        except Exception as err:
            print(err);
        finally:
            self.__RunThread  = None;
            self.__StartLocker.release();





    
if(__name__ =="__main__"):
    import time;
    def OnStarted(evt):
       print("Server started at : {0}:{1}".format(evt.Socket.HostAddress, evt.Socket.Port));

    def OnAccepted(evt):
        print("Connection Request Accepted");

    def OnClosed(evt):
        print(evt.InnerException);
        
       
    def run(port):
        server = SocketServer(port = port);
        server.Started  += OnStarted;
        server.Accepted += OnAccepted;
        server.Closed  += OnClosed;
        server.Start();
        try:
            print("Start...");
            time.sleep(2);
            while(server.IsRunning):
                
                pass;
            print("Completed");
        except Exception as err:
            print("Stop unexceptedly - {0}".format(err));
        finally:
            server.Stop();

    run(8082);
        

    
  
        

