import io;
import os;
import struct;


class BinaryReader:

    def __init__(self, filename):
        self.__IsFile = False;
        stream  = None;
        self.__Filename =  None;
        if(type(filename) == str):
            if(os.path.exists(filename) != True):
                  raise ValueError("{0} does not exists".format(filename));
            self.__Filename    = filename;
            self.__Extension  = os.path.splitext(self.__Filename)[1][1:];
            stream = open(self.__Filename, 'rb');
            self.__IsFile  =  True;
        elif(isinstance(filename , io.BytesIO)):
            stream  = filename;
        self.__Stream = stream;
        
    @property
    def IsFile(self):
        return self.__IsFile;

    def Open(self):
        status = False;
        try:
            self.__Stream = open(self.__Filename, 'rb');
            status  = True;
        except (ValueError ) as err:
            status = False;

        self.IsFile  =  status;
        return status;

    @property
    def Filename(self):
        return self.__Filename;

    @property
    def Extension(self):
        return self.__Extension;

    def Seek(self, pos, where  = io.SEEK_EOF):
        newpos  =  None;
        if(self.Stream != None):
            self.Stream.seek(pos,where);
            newpos  = self.Tell();
        return newpos;

    def Tell(self):
        pos = -1;
        if(self.Stream != None):
          pos = self.Stream.tell();
        return pos;

    def ReadInt64(self):
        value = None;
        if(self.Stream != None):
            value  = np.fromfile(self.Stream, dtype = np.dtype(np.int64), count =1)[0];
            
        return value;

    @property
    def Stream(self):
         return self.__Stream;
      

    def ReadInt32(self):
        value  =  None;
        if(self.Stream != None):
            value  =  np.fromfile(self.Stream, dtype= np.dtype(np.int32), count= 1)[0];
        return value;

    def ReadInt(self):
        return self.ReadInt32();

    def ReadUInt(self):
        value =  None;
        if(self.Stream != None):
            data    = self.Stream.read(2);
            value   =  struct.unpack('H', data)[0];           
        return value;

    def ReadFloat32(self):
         value  = None;
         if(self.Stream != None):
             value     = np.fromfile(self.Stream, dtype=np.dtype(np.float32), count =1)[0];
         return value;

    def ReadFloat(self):
         value = None;
         if(self.Stream != None):
             value = self.ReadFloat32();
         return value;
    
    def ReadInt16(self):
            value  = None;
            if(self.__file != None):
                data   =  self.Stream.read(2);
                value  =  struct.unpack('h', data)[0];
            return value;

    def ReadInt8(self):
        value = None;
        if(self.Stream != None):
            byte  =  self.Stream.read(1);
            value =  ord(byte);
        return value;
          
    def ReadString(self):
        strvalue = "";
        strLength  = self.ReadInt32();
        #do not read the null char 
        for count in range(0, (strLength -1)):
            char16_t  = self.ReadInt16();
            strvalue +=(str(chr(char16_t)));
        return strvalue;


    def Close(self):
        if(self.Stream  != None):
            if(self.IsFile):
                self.Stream.close();
        self.Stream = None;

    def EOF(self):
        status = False;
        if(self.Stream != None):
            pos  =  self.Stream.tell();
            self.Stream(0, io.SEEK_END);
            size  = self.Stream.tell();
            self.Stream.seek(0,io.SEEK_SET);
            status = (pos >= size);
        return status;
