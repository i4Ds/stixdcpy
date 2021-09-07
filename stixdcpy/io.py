#!/usr/bin/python
import numpy as np
'''
    Methods in this module allow to save/load  objects to/from  npy  files

    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
ALLOWED_EXTENSIONS=['.pickle','.npy','.h5','.fits']

class IO(object):
    '''
        Base object
    '''
    def __init__(self):
        pass
    def save(self, data, filename):
        print("this feature has not been implemented!")
        pass


    def load(self,filename):
        print("this feature has not been implemented!")
        pass

        



