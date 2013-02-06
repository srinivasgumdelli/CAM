'''
 start.py
 Copyright (c) 2005 MONTANA STATE UNIVERSITY 
 All Rights Reserved.

 Permission to use, copy, modify, distribute, and sell this software
 and its documentation is hereby granted without
 fee, provided that the above copyright notice appear in all copies
 and that both that copyright notice and this permission notice
 appear in supporting documentation, and that the name of MONTANA STATE UNIVERSITY
 not be used in advertising or publicity pertaining to
 distribution of the software without specific, written prior
 permission.  MONTANA STATE UNIVERSITY makes no representations about the
 suitability of this software for any purpose.  It is provided "as
 is" without express or implied warranty. 

 MONTANA STATE UNIVERSITY DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
 SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
 FITNESS, IN NO EVENT SHALL MONTANA STATE UNIVERSITY BE LIABLE FOR ANY
 SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
 AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING
 OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
 SOFTWARE.

 Author: Srinivas Prasad Gumdelli, gumdelli@cs.montana.edu.  */
'''

import time
import socket
import os

global IPERF,WBEST,ASSOLO,MULTIQ, BUSY, FREE, PING, START_CAPTURE,END_CAPTURE
IPERF = 1
WBEST = 2
ASSOLO = 3
MULTIQ = 4
BUSY = 70985
FREE = 70986
PING = 75896
START_CAPTURE = 12345
END_CAPTURE = 23456



############################################################################
#############   methods for multiQ implementation   ########################  
############################################################################
#def transferFile(fname,HOST):
    
    
#method that does the file transfer over listener process
def get_file(s, file_name):


    print get_file(s, 'file1')
    print get_file(s, 'file2')
    s.sendall('end\n')

def uploadFiles(folder,dcip,PORT,filetype):
    os.chdir(folder)
    dirList = os.listdir(folder)
    print dirList
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect((dcip, int(PORT)))
#    print dirList
    for fname in dirList:
        
        if fname.endswith(str(filetype)):
            cmd = 'get\n%s\n' % (fname)
            ms.sendall(cmd)
            r = ms.recv(2)
            while 1:
                data = ms.recv(1024)
                if not data: 
                    break
            ms.sendall('ok')
            ms.sendall(data)
    
    ms.close()
            
#method to download files recursively using wget
def downloadFiles(dc_ip):
    #check if test directory exists on the system, if not create and chdir to the test dir
    os.chdir(os.getenv("HOME"))
    directory = "testdownload"
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    command = "wget -r -A \"test*.bin\"  http://" + str(dc_ip) + "/download/"
    os.system(command)
#////////////////////////end multiQ methods implementation

def pingDC(dc_ip,port,details):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((dc_ip,port))#send message with code 75896, port is static here, may need to be dynamically extracted from server as well
    client_socket.send(str(details))
#    data = client_socket.recv(256)
#    if int(data) == 65285:#receive confirmation with 65285
#        return 1
#    else:
#        return 0
#    client_socket.close()
    return client_socket
#########################################################################
#                experiment method definitions                          #
#########################################################################
def iperf(port,dcip,sock):
#Method to perform Iperf experiment
    #send packet with IPERF option in it
    sock.send(str(IPERF))
    filename='iperf_' + str(time.time()) + '.txt'
    os.system('touch ' + filename)
    #os.system('iperf -c -p %s %s >> %s',(port,dcip,filename))
    command ='iperf -c ' + dcip + ' >> ' + filename
    os.system(command)
    time.sleep(30)

def assolo(port,dcip,sock):
#Method to perform assolo experiment
#send packet with data 2 in it
    print "assolo"
    sock.send(str(ASSOLO))
    command_assolo = 'sh ./script.sh ' + str(dcip) + str(port)
    print command_assolo
    os.system(command_assolo)
    time.sleep(30)# for delaying the experiment by 30 seconds
    killprocesses()

def multiQ(port,dcip,sock):
#Method to perform the multiQ operation 
#send message to the server to DC packet capture process
    sock.send(str(MULTIQ))
    prevdir = os.getcwd()
    print prevdir
    os.chdir(os.getenv("HOME"))
    directory = "testdownload"
    if not os.path.exists(directory):
        os.makedirs(directory)

    os.chdir(str(os.getenv("HOME")) + "/"+ directory)
    #send msg to dc to initiate packet capture
    #download files
    #send download initiation packet
#    sock.send(str(START_CAPTURE))#send download START packet
    downloadFiles('127.0.0.1')#change to dcip
#    sock.send(str(START_CAPTURE))#send download end packet    
    #then upload the files to the server using listener process
    #send upload initiation packet
    CPORT = 36252
    MPORT = 36251#get dynamic port from server
    home = os.getenv("HOME")
    folder = str(home + "/" + directory + "/" +str(dcip)+ "/download")
    print folder
    sock.send(str(START_CAPTURE))#send UPLOAD START packet
    uploadFiles(folder,dcip,CPORT,MPORT,'.bin')
    #send upload end packet
    sock.send(str(END_CAPTURE))
    os.chdir(prevdir)

def wBest(host, port,sock):
    sock.send(str(WBEST))
    command = "sh ./wbest.sh host"
    os.system(command)
    time.sleep(30)
    
def killprocesses():
#kills the processes that were created for the assolo measurements
    command = "kill -9 `pidof assolo_rcv`"
    os.system(command)
    command = "kill -9 `pidof assolo_snd`"
    os.system(command)
    command = "kill -9 `pidof assolo_run`"
    os.system(command)
    command = "kill -9 `pidof iperf`"
    os.system(command)

def getInfo(host,port):
#gets port and data center IP information from server
    #initial data
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host,port)) #Connect to the DB server
    client_socket.send(str(BUSY)) #send HI message to the server, Change localhost to the server's address and port
    
    data = client_socket.recv(256) #waiting to receive OK message from the server
    details = data.split('@')
    client_socket.close()
    return details

##############################################################################
######################      main program starts here     #####################
##############################################################################
def main():
    host_db = "dknight.eps.montana.edu"#ip or address of the database server
    port_db = 33235#port of the database server
    port_dc = 33456
    details = getInfo(host_db,port_db)#contact database server
    address_dc = 'localhost'#details[3]
    sock = pingDC(address_dc,port_dc,details)
    iperf(details[0],address_dc,sock)
    assolo(details[1],address_dc,sock)
    multiQ(details[2],address_dc,sock)
    wBest(details,address_dc,sock)
    #send done message to the server, releases the ports
    #connect to dbserver and send message
    client_socket.sendto(FREE,(host_db,port_db)) #dbserver, change to TCP
    #connect to the datacenter before sendto # changed to TCP!!
    uploadFiles(str(os.getcwd()),'54.241.35.209','36250','36252','.txt')#server address, upload file to the server
    uploadFiles('/home/gumdelli/testdownload/184.169.155.37/download','127.0.0.1','36250','.bin')#server address, upload file to the server
    
if  __name__ =='__main__':
    main()
    
