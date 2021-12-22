#!/usr/bin/python
import numpy as np
import pandas as pd

from stixdcpy.logger import logger
'''
    Methods in this module allow to save/load  objects to/from  npy  files

    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
ALLOWED_EXTENSIONS = ['.pickle', '.npy', '.h5', '.fits']
import joblib


class IO(object):
    """
        Base object
    """
    def __init__(self):
        pass

    def dump(self, data, filename):
        """Dump object to joblib file
        Args
            data: object
                data object
            filename: str
                filename

        Returns:
            filename: str
                filename
        """
        joblib.dump(data, filename)
        return filename
        #logger.error("this feature has not been implemented!")
        #pass

    def load(self, filename):
        """load object from file

        Args:
            filename:  str

        Returns:
            data: object


        """
        return joblib.load(filename)
        #logger.error("this feature has not been implemented!")
        #pass

    def to_pandas(self):
        if self.data:
            return pd.DataFrame(self.data)
        return None
