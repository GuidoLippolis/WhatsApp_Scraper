# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 09:29:25 2022

@author: guido
"""

class AudioNotFoundException(Exception):
    def __init__(self, value):
        self.value = value