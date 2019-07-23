"""
by @MohammadRaziei
"""
import select 
import queue 
from collections import namedtuple
from time import sleep
from socket import *
person = namedtuple('person', ['name','id','mode','cnn_ip'])
users_index=0
counter=0
serverPort = 12500
inputs=[]
outputs=[]
exp=[]
users=[]
Conn = socket(AF_INET,SOCK_STREAM)
Conn.bind(('',serverPort))
Conn.listen(5)
inputs.append(Conn)
exp.append(Conn)
message_queues={}
print ('The server is ready to receive')
while 1:   
    readable, writable, exceptional = select.select(inputs,outputs,exp)
    for sock in readable :
        if sock is Conn:
            connectionSocket, addr = Conn.accept()
            inputs.append(connectionSocket)
            exp.append(connectionSocket)
            users.append(person(name="",id=users_index,mode='',cnn_ip=connectionSocket)) 
            message_queues[connectionSocket] = queue.Queue()
            users_index+=1
            counter+=1
            print ('{} user(s) connected to server.'.format(counter))
        else:
            msg = sock.recv(1024)
            msg = msg.decode(encoding='UTF-8',errors='strict')
            if msg.__le__(''): # hengame khorroj client payam khali mifrestad ke dar inja handle mishavad                
                z=[x.id for x in users if x.cnn_ip==sock]
                # remove index and shift list
                for x in range(z[0],users_index):
                    users[x]=users[x]._replace(id=users[x].id-1) 
                print(''.join([users[z[0]].name,' Left']))
                x=person(name=users[z[0]].name,id=users[z[0]].id,mode=users[z[0]].mode,cnn_ip=sock)
                users.remove(x)
                exceptional.append(sock)
                break
            if msg[0]=="$": #ozv shodan
                 sock.send(bytes(''.join(['Hi ',msg[1:], ' ! :)']),'UTF-8'))
                 print(''.join([msg[1:], ' Joined']))
                 z=[x.id for x in users if x.cnn_ip==sock]
                 users[z[0]]=users[z[0]]._replace(name=msg[1:])
            elif msg[0]=="~": #tayeen e mode
                 z=[x.id for x in users if x.cnn_ip==sock]    
                 users[z[0]]=users[z[0]]._replace(mode=msg[1])
            elif msg=="__fetch__":
                writable.append(sock) 
            else :
                # ezafe kardane be Queue
                z=[x.id for x in users if x.cnn_ip==sock]
                msg=''.join([users[z[0]].name," : ",msg])
                for x in users:
                    message_queues[x.cnn_ip].put(msg)   
        #print(users[:])  # check kardane dorost ezfe kardan e object be ezye ashkhas
    for sock in writable:
        l= message_queues[sock].qsize()
        sock.send(bytes(str(l),'UTF-8'))
        for c in range(0,l):
            sock.send(bytes(message_queues[sock].get_nowait(),'UTF-8'))
            #set a time out
            sleep(0.05)			
			
    for sock in exceptional:
        # Stop listening for input on the connection
        inputs.remove(sock)
        exp.remove(sock)
        if sock in outputs:
            outputs.remove(sock)
        sock.close()
        # Remove message queue
        del message_queues[sock]
        users_index-=1
        counter-=1
        print ('%d user(s) connected to server.'%counter)
        