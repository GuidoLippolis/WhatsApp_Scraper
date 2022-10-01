# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 22:33:59 2022

@author: guido
"""

import tkinter as ttk
from view import View

class App(ttk.Tk):
    def __init__(self):
        super().__init__()

        self.title('WhatsApp Scraper')
        self.geometry("900x625")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        # create a view and place it on the root window
        view = View(self)
        view.grid(row=5, column=0, padx=10, pady=10, stick='W')
        
        vsbar = ttk.Scrollbar(view, orient=ttk.VERTICAL)
        vsbar.place(x=868, y=279, height=280, width=20)
        
        # style = ttk.Style(view)