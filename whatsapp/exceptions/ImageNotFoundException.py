# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 09:28:40 2022

@author: guido
"""

class ImageNotFoundException(Exception):
    def __init__(self, value):
        self.value = value