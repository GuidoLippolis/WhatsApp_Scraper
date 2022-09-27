# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 21:52:39 2022

@author: guido
"""

class ImageNotFoundException(Exception):
    def __init__(self, value):
        self.value = value
        
class VideoNotFoundException(Exception):
    def __init__(self, value):
        self.value = value
        
class AudioNotFoundException(Exception):
    def __init__(self, value):
        self.value = value
        
class DocumentNotFoundException(Exception):
    def __init__(self, value):
        self.value = value
        
