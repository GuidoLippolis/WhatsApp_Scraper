# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:59:49 2022

@author: guido
"""

class ArchivedChatsButtonNotFoundException(Exception):
    def __init__(self, value):
        self.value = value