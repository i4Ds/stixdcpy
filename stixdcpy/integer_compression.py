"""
This script provides functions for decompressing integer values and creating error lookup tables.

It includes the following functions:

- decompress(x, K, M): Decompresses a compressed integer value.
- make_lut(k, m): Creates a lookup table for error calculation based on k and m values.

Additionally, it defines error lookup tables for specific combinations of k and m values.

Author: Hualin Xiao(hualin.xiao@fhnw.ch)

"""

import numpy as np

MAX_STORED_INTEGER = 1e8



class Compression(object):
    def __init__(self, k,m, with_stat_error=True):
        self.lut=Compression.get_error_lut(k,m, with_stat_error)

    def get_error(self,counts):
        return self.lut[int(counts)]

    @staticmethod
    def decompress(x,S, K, M):
        """
        Decompresses a compressed integer value.

        Parameters:
            x (int): The compressed integer value to decompress.
            K (int): The number of bits reserved for the exponent.
            M (int): The number of bits reserved for the mantissa.

        Returns:
            tuple: A tuple containing the error and the decompressed value.
                   The error represents the uncertainty in the decompressed value.
                   The decompressed value is the original integer value.
        """
        if S + K + M > 8 or S not in (0, 1) or K > 7 or M > 7:
            return None, None
        if K == 0 or M == 0:
            return None, None

        sign = 1
        if S == 1:  # signed
            MSB = x & (1 << 7)
            if MSB != 0:
                sign = -1
            x = x & ((1 << 7) - 1)

        x0 = 1 << (M + 1)
        if x < x0:
            return None, x
        mask1 = (1 << M) - 1
        mask2 = (1 << M)
        mantissa1 = x & mask1
        exponent = (x >> M) - 1
        # number of shifted bits
        mantissa2 = mask2 | mantissa1  # add 1 before mantissa
        low = mantissa2 << exponent  # minimal possible value
        high = low | ((1 << exponent) - 1)  # maximal possible value
        mean = (low + high) >> 1  # mean value
        error = np.sqrt((high - low) ** 2 / 12)
        #error of a flat distribution

        if mean > MAX_STORED_INTEGER:
            return error, float(mean)

        return error, sign * mean

    @staticmethod
    def get_error_lut(k,  m, with_stat_error=True, s=0):
        """
        Creates a lookup table for error calculation based on k and m values.

        Parameters:
            k (int): The number of bits reserved for the exponent.
            m (int): The number of bits reserved for the mantissa.

        Returns:
            dict: A dictionary mapping decompressed values to their respective errors.
        """
        res = {}
        for i in range(256):
            err, val = Compression.decompress(i,s, k, m)
            if err is not None:
                res[val] = np.sqrt(err ** 2 + val) if with_stat_error else err
        return res

    #error_luts = {'035': make_lut(3, 5), '044': make_lut(4, 4), '053': make_lut(5, 3)}

#if __name__ == '__main__':
#    from pprint import pprint
#    pprint(error_luts)

