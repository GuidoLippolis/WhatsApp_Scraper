# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 22:33:59 2022

@author: guido
"""

import tkinter as tk
from view import View

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Tkinter MVC Demo')
        self.geometry("900x625")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        # create a view and place it on the root window
        view = View(self)
        view.grid(row=0, column=0, padx=10, pady=10)