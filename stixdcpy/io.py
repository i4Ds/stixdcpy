#!/usr/bin/python
import joblib
import numpy as np
import pandas as pd

from stixdcpy.logger import logger
ALLOWED_EXTENSIONS = ['.pickle', '.npy', '.h5', '.fits']

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
        # pass

    def load(self, filename):
        """load object from file

        Args:
            filename:  str

        Returns:
            data: object


        """
        return joblib.load(filename)
        #logger.error("this feature has not been implemented!")
        # pass

    def to_pandas(self):
        if self.data:
            return pd.DataFrame(self.data)
        return None
