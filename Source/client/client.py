# Amirreza Hosseini 9820363
# Porject: FTP protocol

import socket
from os import system
import sys
from colorama import Fore


def command_table_hash():
    command_table = {"EXIT": b'0', "LIST": b'1',"DWLD": b'2', "PWD": b'3', "CD": b'4'}
                          
    return command_table


help_msg = """
welcome to ftp client.
call one of the following functions: 

commands:
help             : display this manual
list             : display a list of files and their size and directories(directories start with >)
pwd              : print workspace directory
cd {file name}   :   change directory to {file name}
dwld {file_path} : download file_path
Exit             :  close the client
"""


def rec_command():
    in_str = input("enter command# ")
    command_list = in_str.split(" ")
    command = command_list[0]
    after_command_str = command_list[-1]
    if(command_list[0] == command_list[-1]):
        after_command_str = ""
    command = command.upper()
    return command, after_command_str


def LIST(client: socket, list_flag: bytes):
    client.send(list_flag)
    msg_size = client.recv(4)
    msg_size = int.from_bytes(msg_size, 'big')
    msg_bytes = client.recv(msg_size)
    msg = msg_bytes.decode('utf-8')
    print(msg)


def PWD(client: socket, list_flag: bytes):
    client.send(list_flag)
    msg_bytes = client.recv(512)
    msg = msg_bytes.decode('utf-8')
    print(msg)


def CD(client: socket, list_flag: bytes, FILE):
    client.send(list_flag)
    client.send(bytes(FILE, 'utf-8'))
    msg_bytes = client.recv(512)
    msg = msg_bytes.decode('utf-8')
    print(msg)


def DWLD(client: socket, list_flag, FILE):
    client.send(list_flag)
    client.send(bytes(FILE, 'utf-8'))
    port = int.from_bytes(client.recv(4), "big")
    if port != 0:
        size = int.from_bytes(client.recv(4), "big")
        data_ch = socket.socket()
        data_ch.connect(("127.0.0.1", port))
        file = b''
        while size > 0:
            buffer_size = 4096
            file += data_ch.recv(buffer_size)
            size -= buffer_size
        print("recived.")
        f = open(FILE, "wb")
        f.write(file)
        f.close()
        data_ch.close()
    else:
        print(client.recv(25).decode('utf-8'))



command_table = command_table_hash()
#normal version
#address = ("127.0.0.1", 2121)

#ngrok vesion
address = ("4.tcp.eu.ngrok.io", 10080)

client = socket.socket()
client.connect(address)


while(True):
    command, FILE = rec_command()
    if command == "EXIT":
        client.send(command_table["EXIT"])
        client.close()
        break
    elif command == "HELP":
        print(help_msg)
    elif command == "LIST":
        LIST(client, command_table["LIST"])
    elif command == "PWD":
        PWD(client, command_table["PWD"])
    elif command == "CD":
        if FILE == "":
            FILE = input("enter file:")
        CD(client, command_table["CD"], FILE)
    elif command == "DWLD":
        if FILE.find("/") != -1:
            FILE = ""
            print("file name cant contain /")
        if FILE == "":
            FILE = input("enter file:")
        DWLD(client, command_table["DWLD"], FILE)
    else:
        print("wrong command type! Use help")
client.close()
