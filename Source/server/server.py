# Amirreza Hosseini 9820363
# Porject: FTP protocol

from random import randint
import socket
import os
import sys

os.chdir("files")
PAth = os.getcwd()


def eval_name_file(file_name):
    pass

#abslute path to realtive path
def dir_name_maker(path):
    path=path[len(PAth):]
    if path=='':
        path='/'
    return path

class client:
    
    #client constructor
    def __init__(self,client:socket):
        self.client=client
        
    def LIST(self):
        print("receive list request\n")
        Dir=[]  #list of relative path directories
        file=[] #list of tuple (filename,size) all ./ files
        files_size=0
        direntry=os.scandir(".")
        for item in direntry:
            if item.is_dir():
                Dir.append(item.name)
            if item.is_file():
                item_name = item.name
                file.append((item_name,os.stat(item_name).st_size))# append (name,size) to files list
                files_size+=os.stat(item_name).st_size             #calculate size of all files
        output_str=""
        #making massage to string
        for i in file:
            output_str+=f"{i[0]:20}{i[1]}\n"
        for i in Dir:
            output_str+=f">{i}\n"
        output_str+=f"all files size:{files_size}"
        # return massage in bytes format and size of massage
        return bytes(output_str,'utf-8'),len(output_str)
    
    #send list of files and directories to client
    def ch_dir(self):
        print("receve change directory request\n")
        new_dir_Bytes=self.client.recv(512)
        new_dir=new_dir_Bytes.decode('utf-8')#convert bytes to string
        current_path=os.getcwd()
        try:
            os.chdir(new_dir)
            new_path=os.getcwd()
            if new_path.find(PAth)!=0:# newpath must start with PAth else it is out of server files
                os.chdir(current_path)# back to the first directory and undo changes
                raise FileNotFoundError
            print(f"change directory to {dir_name_maker(os.getcwd())}\n")
            self.client.send(bytes(dir_name_maker(new_path),'utf-8'))
        except FileNotFoundError:
            print("change directory failed:directory not found\n")
            self.client.send(bytes("directory not found",'utf-8'))
            return 0
    def send_file(self):
        try:
            print("receve download request\n")
            file_name_bytes=self.client.recv(64)
            file_name=file_name_bytes.decode('utf-8')
            print("file name recived\n")
            file_stat=os.stat(file_name)
            port=randint(3000,5000)
            print("make a data chanel")
            host=socket.socket()
            host.bind(("127.0.0.1",port))
            host.listen()
            self.client.send(port.to_bytes(4,'big'))
            print("port number sent")
            self.client.send(bytes(file_stat.st_size.to_bytes(4,'big')))
            Data_ch,addr=host.accept()
            print(" start data chanel")
            f=open(file_name,"rb")
            Data_ch.sendfile(f)
            print("file sent")
            f.close()
            Data_ch.close()
            host.close()
        except FileNotFoundError:
            print("file not found") 
            self.client.send(b'\x00\x00\x00\x00')#send int 0  to client for error
            self.client.send(bytes("file not found",'utf-8'))
            return
        except:
            print("error")
            self.client.send(b'\x00\x00\x00\x00')#send int 0  to client for error
            self.client.send(bytes("error",'utf-8'))


    def recive_command(self):
         print("start recive command\n")
         command_hash_table={b'0':"EXIT",b'1':"LIST",b'2':"DWLD",b'3':"PWD",b'4':"CD"}
         while(True):
            command_byte=self.client.recv(1)
            if command_byte==b'':
                print("timeout")
                break
            if command_hash_table[command_byte]=="LIST":
                msg_bytes,size=self.LIST()
                print("sending data\n")
                self.client.send(size.to_bytes(4,'big'))#send int of size of message
                self.client.send(msg_bytes)
            elif command_hash_table[command_byte]=="DWLD":
                self.send_file()
            elif command_hash_table[command_byte]=="PWD":
                wd=dir_name_maker(os.getcwd())
                self.client.send(bytes(f"{wd}\n",'utf-8'))
            elif command_hash_table[command_byte]=="CD":
                print("change directory\n")
                self.ch_dir()
            elif command_hash_table[command_byte]=="EXIT":
                self.client.close()
                break


address=("127.0.0.1",2121)
server=socket.socket()
server.bind(address)
print("server is ready\n")
print("Welcome to the FTP server.\n\nTo get started, connect a client.")
server.listen()
(clientsocket,address)=server.accept()
print(f"new connection start at port {address}\n")
client=client(clientsocket)
client.recive_command()
print("end of connection\n")
server.close()

    
