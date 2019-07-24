# -*- coding: utf-8 -*-
import numpy as np
import os

import _thread as thread




def main():
    N = load_vec(os.path.join( os.getcwd(), 'adj_mat.txt'),0).size
    for i in range(N):
#        thread.start_new_thread(  os.system, ("cmd /k echo %cd%", ) )
        thread.start_new_thread(  os.system, ("cmd /K python start.py", ) )
#        thread.start_new_thread(  os.system, ('cmd /K echo python "'+os.path.join(os.getcwd(), "bell.py") + '"', ) )
   
    print("{} terminal opened :)".format(N))

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
        error("this router number is invalid")        
    return matrix[Num-1,:]



def error(*arg):
    print(*arg)
    
if __name__ == "__main__" :
    main()
