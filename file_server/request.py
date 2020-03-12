import io;
import struct;
from binaryreader import BinaryReader;



class Parser(object):

    def Parse(self, data:bytearray):
        if(type(data) != bytearray):
            raise TypeError("@Expecting a data array");

class RequestType(int):
    HEART_BEAT  = 0x0000;


class PacketParserByteBase(object):
    
    @property
    def Bytes(self):
        return  b'';
    
        
class Version(object):

    def __init__(self, major:int, minor:int, build:int):
        self.__Major  =  major;
        self.__Minor  = minor;
        self.__Build  = build;

    @property
    def Major(self):
        return self.__Major;

    @property
    def Minor(self):
        return self.__Minor;

    @property
    def Build(self):
        return self.__Build;
    
        
class Header(PacketParserByteBase):

    def __init__(self, **kwargs):
        super().__init__();
        self.__Version          = Version(1,0,000);
        self.__RequestType      = 0x0000;
        self.__IpAddressLength  = 0x00;
        self.__IpAddress        = ""; # A String type of IpAddressLength
        self.__MacAddressLength = 0x00;
        self.__MacAddress       = ""; # The computer that send the request mac address
        self.__ComputerNameLength = 0x00;
        self.__ComputerName     = ""; # The computer that send the request Name
        self.__ContentLength    = 0x0000;


    @property
    def Version(self):
        return self.__Version;

    @Version.setter
    def Version(self, version:Version):
        if(isinstance(version , Version) is not True):
            raise TypeError("Expecting a version object");
        self.__Version  =  version;

    @staticmethod    
    def Parse(buffer: io.BytesIO , length: int = 0):
        if(isinstance(buffer, io.BytesIO) is not True):
            raise TypeError("Expecting  buffer type  but {0} given".format(type(buffer)));
        #Start bytes parsing
        header =  None;
        current_pos =  buffer.tell();
        buffer.seek(0, io.SEEK_END);
        length_from_pos  = buffer.tell();
        buffer.seek(current_pos, io.SEEK_SET);

        if(length_from_pos > 0):
            reader  =  BinaryReader(buffer);
            major_value  =  buffer.Read8Bits();
            minor_value  =  buffer.Read8Bits();
            build_value  =  buffer.Read16Bits();

            version = Version(major_value, minor_value, build_value);
            
            
            
            header  =  Header(version = version , );        
        
        

        return header;
        
        

class Content(PacketParserByteBase):
    def __init__(self,**kwargs):
        super().__init__();
        self.__Text = kwargs['text'] if ('text' in kwargs) else '';
        
    @property
    def Text(self):
        return self.__Text;

    @staticmethod
    def Parse(buffer: io.BytesIO):
        if(isinstance(buffer, io.BytesIO) is not True):
            raise TypeError("@Parse: expecting a io.BytesIO");
        content  =  None;

        return content;
    
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
                    header   =  Header.Parse(buffer);                   
                    content  =  Content.Parse(buffer);
                    request  =  Request(header, content);
            
        except Exception as err:
            raise;
        return request;



if(__name__ =="__main__"):
    request  =  None;

    
