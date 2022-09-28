# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:11:04 2022

@author: guido
"""

class EmptyChatException(Exception):
    def __init__(self, value):
        self.value = value