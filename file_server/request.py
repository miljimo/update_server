import io;


class Parser(object):

    def Parse(self, data:bytearray):
        if(type(data) != bytearray):
            raise TypeError("@Expecting a data array");

class RequestType(int):
    HEART_BEAT  = 0x0000;
    
"""
  Version           : 2bytes
  Packat-Id         : 2bytes
  Session-Length    : 1bytes;
  Session-UID       : 
  Offset            : 2bytes;
"""

class DoParserObject(object):
    
    def __init__(self, buffer:io.BytesIO):
        if(isinstance(buffer, io.BytesIO) is not True):
            raise TypeError("@DoParseObject : expecting a io.BytesIo object");
        self.DoParse(buffer);

    def DoParse(self, buffer):
        print("What can I do");
        pass;

    @property
    def Bytes(self):
        return  b'';
    
        
    
class Header(DoParserObject):

    def __init__(self,buffer:io.BytesIO):
        super().__init__(buffer);
        self.__Version     = 0x00;
        self.ContentLength = 0x0000;

    def DoParse(self, buffer):
        print("Hello I am the header");

class Content(DoParserObject):
    def __init__(self, buffer:io.BytesIO):
        super().__init__(buffer);
    
class Request(Parser):

    def __init__(self, header :Header ,  content : Content):
        self.__Header   =  header if (isinstance(header, Header))   else None;
        self.__Content  =  content if(isinstance(content, Content)) else None;
        self.__Buffer   = None;
        self.__Error    =  None;
    @property
    def Header(self):
        return self.__Header;

    @property
    def Content(self):
        return self.__Content;


    @property
    def Bytes(self):
        return self.Header.Bytes + self.Content.Bytes;

    @staticmethod
    def Parse(raw_bytes:bytearray):
        request = None;
        try:
            if(len(raw_bytes) <= 0) and (type(raw_bytes) != bytearray):
                raise TypeError("@Request Expecting a byte array");
            buffer =  io.BytesIO(raw_bytes);
            
            if(buffer != None):
                length  =  buffer.seek(0, io.SEEK_END);
                size    =  buffer.tell();
                buffer.seek(0, io.SEEK_SET);
                if(size > 0):
                    header   =  Header(buffer);                   
                    content  =  Content(buffer);
                    request  =  Request(header, content);
            
        except Exception as err:
            raise;
        return request;
