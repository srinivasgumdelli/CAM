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

import time, socket, os, ftplib, urllib, re, platform,random

global IPERF,WBEST,ASSOLO,MULTIQ, BUSY, FREE, PING, START_CAPTURE,END_CAPTURE
IPERF = 1
WBEST = 2
ASSOLO = 3
MULTIQ = 4
PATHLOAD = 5
BUSY = 70985
FREE = 70986
PING = 75896
START_CAPTURE = 12345
END_CAPTURE = 23456
FOLDER = ''


############################################################################
#############   methods for multiQ implementation   ########################  
############################################################################
def packetTransfer(dc_ip):#sends various packets in 10 fold size starting with 1500
    size = 1500
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(dc_ip)
    for i in range(0,10):
        data=''
        for i in range(0,size):
            data += random.randrange(0,9)
        sock.sendall(data)
        size = size + 1500
    sock.close()
        
def upload(folder,ip,filetype):
    os.chdir(folder)
    dirList = os.listdir(folder)
    print dirList
    ftp = ftplib.FTP('54.241.35.209')
    ftp.login('nlab','networkslab')
    ftp.cwd('uploads')
    group = re.compile(u'(?P<ip>\d+\.\d+\.\d+\.\d+)').search(urllib.URLopener().open('http://jsonip.com/').read()).groupdict()
    directory = group['ip']
    ftp.mkd(directory)
    for fname in dirList:
        if fname.endswith(str(filetype)):
            f = open(fname,'rb')
            ftp.upload('STOR '+str(fname),f)
    
#method that does the file transfer over listener process

def uploadFiles(folder,dcip,PORT,filetype):
    os.chdir(folder)
    dirList = os.listdir(folder)
    print dirList
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print PORT
    ms.connect((dcip, int(PORT)))
    for fname in dirList:
        if fname.endswith(str(filetype)):
            cmd = 'get\n%s\n' % (fname)
            ms.sendall(cmd)
            f = open(fname,'rb')
            data = f.read()
            f.close()
            print fname
#            print data
#            r = ms.recv(2)
            ms.sendall(data)
            ms.sendall('done\n%s\n' %(fname))
    ms.sendall('\nend\n') 
    ms.close()
            
#method to download files recursively using wget
def downloadFiles(dc_ip):
    #check if test directory exists on the system, if not create and chdir to the test dir
    os.chdir(os.getenv("HOME"))
    directory = "testdownload"
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    command = "wget -r -A \"test*.txt\"  http://" + str(dc_ip) + "/download/"
    os.system(command)
#////////////////////////end multiQ methods implementation

def pingDC(dc_ip,port,details):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((dc_ip,port))#send message with code 75896, port is static here, may need to be dynamically extracted from server as well
    client_socket.send(str(details))
    print len(details)
    return client_socket

#########################################################################
#                experiment method definitions                          #
#########################################################################
def iperf(port,dcip,sock):
#Method to perform Iperf experiment
#send packet with IPERF option in it
    print "IPERF"
    sock.send(str(IPERF))
    print (sock.recv(2))
    time.sleep(2)
    filename='iperf_' + str(time.time()) + '.txt'
    os.system('touch ' + filename)
    command ='./executables/'+str(FOLDER)+'/iperf -p '+ str(port)+ ' -c ' + dcip + ' >> ' + filename
    print command
    os.system(command)
    time.sleep(30)

def assolo(port,dcip,sock):
#Method to perform assolo experiment
#send packet with data 2 in it
    print "assolo"
    sock.send(str(ASSOLO))
    sock.recv(2)
    os.system('./executables/'+str(FOLDER)+'/assolo_rcv &')
    os.system('./executables/'+str(FOLDER)+'/assolo_snd &')
    command_assolo = './executables/'+str(FOLDER)+'/assolo_run -R localhost -S ' + str(dcip) +' -t 100 -J 4'
    print command_assolo
    os.system(command_assolo)
    time.sleep(30)# for delaying the experiment by 30 seconds
    killprocesses()

def multiQ(port,dcip,sock):
#Method to perform the multiQ operation 
#send message to the server to DC packet capture process
    sock.send(str(MULTIQ))
    sock.recv(2)
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
    downloadFiles(dcip)#change to dcip
    #then upload the files to the server using listener process
    #send upload initiation packet
    CPORT = 36250
    home = os.getenv("HOME")
    folder = str(home + "/" + directory + "/" +str(dcip)+ "/download")
    print folder
    uploadFiles(folder,dcip,CPORT,'.txt')
    #send upload end packet
#    sock.send(str(END_CAPTURE))
    os.chdir(prevdir)
    sock.send(str(MULTIQ))
    
    
def wBest(port, host, sock):
    sock.send(str(WBEST))
    sock.recv(2)
    command = './executables/'+str(FOLDER)+'/wbest_snd >> '+str(host)+ '_wbest_download_'+str(time.time())+'.txt &'
    os.system(command)
    command = './executables/'+str(FOLDER) + '/wbest_rcv -h ' + str(host) + ' >> ' + str(host)+ '_wbest_upload_'+str(time.time())+'.txt &'
    os.system(command)
    time.sleep(30)
    
def pathLoad(port, host, sock):
    sock.send(str(PATHLOAD))
    sock.recv(2)
    command = './executables/'+str(FOLDER)+'/pathload_snd >> '+str(host)+ '_pathload_download_'+str(time.time())+'.txt &'
    os.system(command)

    command = './executables/'+str(FOLDER)+'/pathload_snd >> '+str(host)+ '_pathload_download_'+str(time.time())+'.txt &'
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
    command = "kill -9 `pidof pathload_rcv`"
    os.system(command)
    command = "kill -9 `pidof pathload_snd`"
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

def setArchitecture():
    line = str(platform.machine())
    global FOLDER
    if line=='x86_64' or line=='X86_64':
        FOLDER = 'X86_64'
    elif line=='i386' or line == 'i686' or line=='i586':
        FOLDER = 'i386'
    else:
        print "Architecture Unknown, cannot continue"
    print FOLDER
        
def changeMode():
    os.system('chmod +x -R ./executables/' +str(FOLDER))
    
##############################################################################
######################      main program starts here     #####################
##############################################################################

def main():
    setArchitecture()
    print FOLDER
    changeMode()
    host_db = "54.241.35.209"#ip or address of the database server
    port_db = 33235#port of the database server
    port_dc = 33456
    details = getInfo(host_db,port_db)#contact database server
    print details
    address_dc = details[3]
    sock = pingDC(address_dc,port_dc,details)
    iperf(details[0],address_dc,sock)
    assolo(details[1],address_dc,sock)
    multiQ(details[2],address_dc,sock)
    wBest(details,address_dc,sock)
    pathLoad(details,address_dc,sock)
    packetTransfer(address_dc)
    #send done message to the server, releases the ports
    #connect to dbserver and send message
    #connect to the datacenter before sendto # changed to TCP!!
    upload(str(os.getcwd()),address_dc,'.txt')
    upload(str(os.getcwd()),address_dc,'.instbw')


if  __name__ =='__main__':
    main()