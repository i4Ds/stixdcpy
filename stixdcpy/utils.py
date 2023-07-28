"""
    This module provides APIs to retrieve STIX preview images from STIX data center , and provides tools to display the data
    """
import sys

def is_notebook():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    return 'ipykernel' in sys.modules

