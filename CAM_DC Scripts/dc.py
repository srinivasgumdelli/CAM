import time, socket, os,random,datetime

#this script is to be run on the Data Centers not the main server

#change the implementation to add threads for each client. Have it setup in such a way that the each client connection is started on a new thread with their respective port number

#have the client send a hello message to the server, the server starts a new thread and have the thread handle the rest of the process, get port numbers and reply the port numbers to the client from the thread itself

#kill the thread once the process is complete
global PING, IPERF, MULTIQ, WBEST, ASSOLO, START_CAPTURE, END_CAPTURE
PING = 75896
IPERF = 1
WBEST = 2
ASSOLO = 3
MULTIQ = 4
PATHLOAD = 5
PACKETTRANSFER = 6


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 33456))

def iperf(addr,port,sock):
    print "iperf"
#    port_iperf=15000
    os.system('./executables/iperf -s -p' + str(port) + ' &')
    sock.send('ok')
#    server_socket.sendto("1", (addr,port))
    
def assolo(addr,port,sock):
    print "assolo"
    os.system('./executables/assolo_rcv &')
    os.system('./executables/assolo_snd &')
    sock.send('ok')
    time.sleep(4)
    os.system('./executables/assolo_run -R localhost -S ' + str(addr)+' -t 100 -J 4')
#    server_socket.sendto("2", (addr,port))

def multiQ(addr,port,sock):
    print "multiQ"
    command = 'sudo tcpdump -i eth0  \'src ' +str(addr) +' and port 80\' -w '+str(addr)+ '_download_' +str(time.time())+'.txt &'
    os.system(command)
    command = 'sudo tcpdump -i eth0  \'src ' +str(addr) +' and port 36252\' -w '+str(addr)+ '_upload_' +str(time.time())+'.txt &'
    os.system(command)
    #start packet capture
    #end packet capture after receiving a packet from client
#    server_socket.sendto("3", (addr,port))
    sock.send('ok')
    sock.recv(1)
    os.system('sudo kill -9 `pidof tcpdump`')
    
def wBest(addr,port,sock):
    print "wBest"
    os.system('./executables/wbest_rcv >> '+str(addr)+ '_wbest_download_'+str(time.time())+'.txt &')
    sock.send('ok')
    time.sleep(2)
    os.system('./executables/wbest_snd -h ' + str(addr) + ' >> '+str(addr)+ '_wbest_upload_'+str(time.time())+'.txt &')
    
def pathLoad(addr,port, sock):
    print "pathLoad"
    sock.send('ok')
    command = './executables/pathload_snd ' + str(addr) + ' >> '+str(addr)+ '_pathload_upload_'+str(time.time())+'.txt &'
    os.system(command)
    time.sleep(2)
    
def packetTransfer(addr,port,sock):
    f = open('./time_'+str(addr)+'.txt','wb')
    socket_pt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection, addr = socket_pt.accept()
    size = 1500
    endsize = 15000
    data =''
    starttimer = datetime.datetime.now()
    while(size<=endsize):
        data += connection.recv(1)
        if len(data)==size:
            endtimer = datetime.datetime.now()
            time = endtimer-starttimer
            starttimer = endtimer
            data=''
            size+=1500
            f.write(str(time)+'\n')
    f.close()
    connection.close()
            
    
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
        
while 1:
    #listen to options
    #after getting request from client, call the appropriate method
    server_socket.listen(100)
    connection,address_client = server_socket.accept()
    client_ip = address_client[0]
    data = connection.recv(43)#gets a ping message with list of ports from the client
    
    iperf_port = data[0]
    assolo_port = data[1]
    multiq_port = data[2]
    wbest_port = data[3]
    pathload_port = data[4]
    transfer_port = data[5]
    
    for i in range(0,6):
        data = int(connection.recv(1))
        print data
        if data ==IPERF:
            iperf(client_ip,iperf_port,connection)
        elif data ==ASSOLO:
            assolo(client_ip,assolo_port,connection)
        elif data == MULTIQ:
            multiQ(client_ip,multiq_port,connection)
        elif data == WBEST:
            wBest(client_ip,iperf_port,connection)#change port
        elif data == PATHLOAD:
            pathLoad(client_ip,pathload_port,connection)
        elif data == PACKETTRANSFER:
            packetTransfer(client_ip,transfer_port, connection)
        
    killprocesses()
    connection.close()