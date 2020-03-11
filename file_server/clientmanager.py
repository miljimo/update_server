from threading import Lock;
from constants import *;


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
            client.Thread.join(WAIT_THREAD_INTERVAL);
            del self.__Clients[ipaddress];            
        self.__Locker.release();
        
    
    @property
    def Count(self):
        return len(self.__Clients);
