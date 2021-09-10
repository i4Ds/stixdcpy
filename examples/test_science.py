import sys

import numpy as np

from stixdcpy.quicklook import LightCurves
from stixdcpy.energylut import EnergyLUT
from stixdcpy import ancillary as anc
from stixdcpy.net import FitsProduct

from stixdcpy.science import L1Product, SpectrogramProduct
from stixdcpy.housekeeping import Housekeeping


from matplotlib import pyplot as plt

from pprint import pprint
sci_data=L1Product.fetch(request_id=2105090003)
sci_data.peek()
plt.show()