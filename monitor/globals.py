

"""
File:           globals.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains global declarations, used throughout the whole project.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import numpy as np

class NotCallableModuleError(Exception):
    """Class, used when not suitable module is called directly.
    """
    def __init__(self):
        super().__init__("This module can not be called like that!")


def normalize(l):
    minimum,maximum = min(l),max(l)
    if maximum > minimum:
        return (np.array(l) - minimum)/(maximum - minimum)
    else:
        return np.array(l)-minimum

# called directly
if __name__ == '__main__':
    raise NotCallableModuleError