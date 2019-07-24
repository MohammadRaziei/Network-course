#!/usr/bin/env python3
import json, os, msvcrt
import socket
from time import sleep
import numpy as np



def main() :
#    num = 1
    adj_mat_file = 'adj_mat.txt'
    ports , numberOfNodes = load_ports(os.path.join( os.getcwd(), 'which_port.txt'))
    num = int(input("which router am I? (number between 1 & {})\t".format(numberOfNodes)))

    init_vec = load_vec(os.path.join( os.getcwd(),adj_mat_file ),num)

    myRouter = Router(num,'localhost',ports,init_vec.copy())
    
#    print(ports)
#    print(init_vec)
    try:
        ss = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        ss.bind(('localhost',ports[num]))   
        print("ok \n Press 'S' to setup")        
    
        wait_for_S()
        ss.settimeout(10)
    except ConnectionError as ex:
        error(ex.args,ex.errno,ex.__context__)
        
    print("Done")
    myRouter.notif_all()


    print('table')
    print(myRouter.row)
#    print('neighbors : ',myRouter.neighbors)
    myRouter.print_neighbors()

    print_table(myRouter.table,'table {}'.format(num))

    while True:
        try:
            while True:
                resp = json.loads( get(ss.recv(2048)) )
                print('resp: ',resp)
                if myRouter.update_table(resp):
                    myRouter.notif_all()
                print()
                print_table(myRouter.table,'table {}'.format(num))
                         
            ss.close()
            
        except:
            print("Checking '"+adj_mat_file+"' :)")
            check_vec = load_vec(os.path.join( os.getcwd(),adj_mat_file ),num)
            if (myRouter.row == check_vec ).all():
                print('Costs not changed!')
                continue
            print('Costs changed suddenly!!')
            print('New Costs are bellow')
            print(check_vec)
            
            myRouter.changeToUpdate(check_vec)
            myRouter.notif_all()
            print("rebell")
            continue
        break














#========================================================================
    

def load_ports(filename):
    try:
        file = open(filename, 'r')
    except:
        error("{}. cannot open".format(filename))
        return
    
    try:
        ports = np.array( [[int(num) for num in line.split(' ')] for line in file ] )
    except:
        error('{} is invalid matrix'.format(filename))
        return
    file.close()
    N,M = ports.shape
    ports = {ports[i,0]:int(ports[i,1]) for i in range(np.size(ports,0))}
    return ports,N
##########
def load_vec(filename,Num):
    try:
        file = open(filename, 'r')
    except:
        error("{}. cannot open".format(filename))
        return
    
    try:
        matrix = np.array( [[np.float(num) if num[0] != 'N'  else np.inf  for num in line.split(' ')] for line in file ] )
    except:
        error("{} is invalid matrix".format(filename))
        return
    file.close()
    row,col = matrix.shape
    if Num > row or Num < 0:
        error("This router number is invalid")        
    return matrix[Num-1,:]

def wait_for_S():
    while True:
        sleep(0.1)
        if msvcrt.kbhit():
            keypress=str(msvcrt.getch().decode('utf-8'))
            if keypress =='s' or keypress=='S':
                break

from terminaltables import SingleTable , DoubleTable

def print_table(table_data,title=None):

    """Return table string to be printed."""
    table_instance = SingleTable(table_data.tolist(), title)
    table_instance.inner_heading_row_border = False
    table_instance.inner_row_border = True
#    table_instance.justify_columns = {0: 'center', 1: 'center', 2: 'center'}
    print (table_instance.table)


#=====================================================================
    
class Router:
    def __init__(self,num,addr,ports,row):
        self.num = num
        self.port = ports[num]
        self.addr = addr
        N = row.size
        self.N = N
        ###
        neighbors = []
        for i in range(N):
            if i == num - 1 or row[i] == np.inf:
                continue
            neighbors.append({'name':i+1,'cost' : row[i],'port':ports[i+1],'ip':'localhost'})
        self.neighbors = neighbors
        ###    
        temp = np.array([[np.inf if(j!=i) else np.inf for i in range(N)]for j in range(N)])
        temp[self.num - 1,:] = row
        self.table = temp
        self.row = row
        
    def print(self):
        print('\n',self.name,'--->',self.port)
        print(self.table)
        print() 
        
    def print_neighbors(self):
        TABLE_DATA = [['#','name','cost','port','ip']]
        count = 0
        for neighbor in self.neighbors:
            count = count + 1
            TABLE_DATA.append([count,neighbor['name'],neighbor['cost'],neighbor['port'],neighbor['ip'] ])
        table_instance = DoubleTable(TABLE_DATA, 'neighbors')
        table_instance.justify_columns[2] = 'right'
        print(table_instance.table)
        print()    
        
        
        
    def update_table(self,resp):
        if (self.table[resp['name']-1,:] == resp['vector']).all():
            return False
        self.table[resp['name']-1,:] = resp['vector']
        #        print(self.num,self.table)
        for k in range (self.N):
            self.table[self.num-1,k] = np.min([(self.row[j] + self.table[j,k]) for j in range(self.N) ])            
        return True
    
    def notif_all(self):
        for neighbor in self.neighbors:
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sendSock:
                sendSock.sendto( put(json.dumps({'name':self.num, 'port': self.port, 'vector':self.table[self.num-1,:].tolist()}) ),(neighbor['ip'],neighbor['port']) )

    def changeToUpdate(self,check_vec):
        self.table[self.num-1,:] = check_vec - self.row[self.num-1] + self.table[self.num-1,:]
        self.row = check_vec
        for k in range (self.N):
            self.table[self.num-1,k] = np.min([(self.row[j] + self.table[j,k]) for j in range(self.N) ])            

    
    
    
def put(message):    
    return bytes(message,'UTF-8')    
def get(resp):
    return resp.decode(encoding='UTF-8',errors='strict')

    
    
def error(*arg):
    print(*arg)
    
if __name__ == "__main__" :
    main()
