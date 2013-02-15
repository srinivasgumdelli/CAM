import socket,os
listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener_socket.bind(('',36250))
f=''

filename = ''
while 1:
    size=0
    print "waiting for client connection"
    listener_socket.listen(100)
    connection,address_client = listener_socket.accept()
    if not os.path.exists(str(address_client[0])):
        os.makedirs(str(address_client[0]))
    currdir = os.getcwd()
    os.chdir('./'+str(address_client[0]))
    data = '' # contains last line of a read block if it didn't finish with \n
    in_get, in_done, reading_file, ended = False, False, False, False
    while not ended:
        print size
        if size==13000000:
            break
        if len(data) > 100:  # < update
            f.write( data )    # <
            size += len(data)
            data = ''          # <
        data += connection.recv(4096)
        i = data.find('\n')
        while i >= 0 and not ended:
            line = data[:i]
            data = data[i+1:]
            if in_get:
                filename = line
                reading_file = True
                f = open(filename,'wb')
                in_get = False
            elif in_done:
                if line != filename:  # done inside file content
                    f.write( 'done\n' + line + '\n' )
                else:
                    f.close()
                    reading_file = False
                in_done = False
            else:
                if line == 'get' and not reading_file:
                    in_get = True
                elif line == 'done':
                    in_done = True
                elif line == 'end' and not reading_file:
                    ended = True
                    break;
                else:
                    f.write( line + '\n' )
            i = data.find('\n')
    os.chdir(currdir)
    connection.close()