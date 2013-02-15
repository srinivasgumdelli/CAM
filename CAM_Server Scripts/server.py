# UDP server example
#this part is responsible to collect data from the client and the data centers and also keep a track of all 
#the ports that are being used on various data centers
import socket
import MySQLdb
import sys
import struct, itertools
global BUSY, FREE
BUSY = 70985
FREE = 70896

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("", 33235))
address_dc = 0
port_dc1 = 0
port_dc2 = 0
con = MySQLdb.connect('localhost', 'root', 'cam@MSU','cam') #change details to the one on DBSERVER
caip='54.241.9.109'
vaip=''

def determinePorts(dc_ip): #this method determines the address and port of the dc that the client has to connect to
    cur = con.cursor()  
    cur.execute("SELECT port FROM measurement_ports WHERE dc_ip=%s AND flag='0' ORDER BY port ASC LIMIT 5",(dc_ip))
    port_open = cur.fetchall()
    ports=list(itertools.chain(*port_open))
    ports=[str(i) for i in ports]
    print ports
    return ports

def updateDB(portslist,ip_dc,ip_client,status): #this method inserts the IP of the client address of dc that the client has connected to into the db
    print portslist
    print ip_dc
    print ip_client
    if status == 'busy':
        try:
            cur = con.cursor()
            cur.execute("UPDATE measurement_ports SET flag='1', client_ip = %s WHERE port = %s AND dc_ip = %s" ,(ip_client,portslist[0],ip_dc))
            cur.execute("UPDATE measurement_ports SET flag='1', client_ip = %s WHERE port = %s AND dc_ip = %s" ,(ip_client,portslist[1],ip_dc))
            cur.execute("UPDATE measurement_ports SET flag='1', client_ip = %s WHERE port = %s AND dc_ip = %s" ,(ip_client,portslist[2],ip_dc))
#            cur.execute("UPDATE measurement_ports SET flag='1', client_ip = %s WHERE port = %s AND dc_ip = %s" ,(ip_client,portslist[3],ip_dc))            
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
    

    elif status == 'free':
        try:
            cur = con.cursor()
            cur.execute("UPDATE measurement_ports SET flag='0', client_ip = '0' WHERE port = %s AND dc_ip = %s" ,(portslist[0],ip_dc))
            cur.execute("UPDATE measurement_ports SET flag='0', client_ip = '0' WHERE port = %s AND dc_ip = %s" ,(portslist[1],ip_dc))
            cur.execute("UPDATE measurement_ports SET flag='0', client_ip = '0' WHERE port = %s AND dc_ip = %s" ,(portslist[2],ip_dc))
#            cur.execute("UPDATE measurement_ports SET flag='0', client_ip = '0' WHERE port = %s AND dc_ip = %s" ,(ip_client,portslist[3],ip_dc))            
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)

while 1:
    print "Server Listening"
    server_socket.listen(100)
    connection,client_address = server_socket.accept()
    data = connection.recv(1024)#gets a ping message from the client

    if int(data) == BUSY:
        ip_dc = struct.unpack('>L',socket.inet_aton(caip))
        ip_dc = ip_dc[0]
        print ip_dc
        ports = determinePorts(ip_dc) #check for open ports and Data Center IP for performing the experiment for the client
        portsList = '@'.join(ports)
        portsList = portsList + "@" + str(caip)
#        details = details.join(ip_int)#doing this for one dc now
#        updateDB(portsList,ip_int)#doing this for one DC now
        connection.sendto(portsList, (client_address[0],client_address[1]))#sends a reply to the client
        ip_client = struct.unpack('>L',socket.inet_aton(client_address[0]))
        ip_client = ip_client[0]
        updateDB(ports,ip_dc,ip_client,'busy')
        
    elif int(data) == FREE:
        updateDB(ports,ip_dc,client_address[0],'free')
    connection.close()
        