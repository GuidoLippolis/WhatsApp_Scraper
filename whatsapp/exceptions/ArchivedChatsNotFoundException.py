# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:01:20 2022

@author: guido
"""

class ArchivedChatsNotFoundException(Exception):
    def __init__(self, value):
        self.value = value