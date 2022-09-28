# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:06:36 2022

@author: guido
"""

class EmptyContactsFileException(Exception):
    def __init__(self, value):
        self.value = value