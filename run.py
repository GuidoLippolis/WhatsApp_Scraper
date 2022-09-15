# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 10:34:17 2022

@author: guido
"""

from whatsapp.whatsapp import Whatsapp
from app import App

# THIS IS THE FILE TO BE RUN ONCE MVC ARCHITECTURE IS DEFINED
# app = App()
# app.mainloop()


inst = Whatsapp()
inst.createCSV()