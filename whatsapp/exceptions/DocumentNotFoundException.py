# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 09:29:35 2022

@author: guido
"""

class DocumentNotFoundException(Exception):
    def __init__(self, value):
        self.value = value