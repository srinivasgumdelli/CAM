import MySQLdb

ip_dc = '921766253'
query = "UPDATE measurement_ports SET flag='0', client_ip = '0' WHERE  dc_ip = " + ip_dc
con = MySQLdb.connect('localhost', 'root', 'srinivasgumdelli','cam') #change details to the one on DBSERVER
cur = con.cursor()
cur.execute(query) 
