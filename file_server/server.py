"""
 Using the comsumer and producer pattern
 to implement a file update server
 that will monitor which file is updated and serve
 it the client application.
 The is a continues live connection
 communication this allow the server
 to send update asynchrously to and from the client and the server
"""

from socket import socket;
from threading import Thread, Lock;
import time;

DEFAULT_PORT_ADDRESS  = 3607;

class DaemonServer(object):

    
    def __init__(self, **kwargs):
        self.__Port  = kwargs['port'] if(('port' in kwargs) and (type(kwargs['port']) == int)) else DEFAULT_PORT_ADDRESS;
        self.__StartLocker  =  Lock();
        self.__RunThread    = None;
        self.__IsRunning    = False;
        self.__CanStart     = False;
        self.__socket       = socket();
        
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
        print("Running Worlking");
        while(self.IsRunning):
            print("Server listening will be here to handler clients");
            pass;

        
        pass;

    def Stop(self):
        self.__StartLocker.acquire();
        try:
            if(self.__IsRunning):
                self.__IsRunning  = False;
                self.__RunThread.join(1);
               
        except Exception as err:
            print(err);
        finally:
            self.__RunThread  = None;
            self.__CanStart   = True;
        self.__StartLocker.release();

    



if(__name__ =="__main__"):
    server = DaemonServer();
    server.Port  = 5617;
    server.Start();

    time.sleep(1);
    server.Stop();
    print("Start again");
    time.sleep(0.5);
    server.IsRunning  = True;
 
    time.sleep(1);
    server.Stop();

