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
        # self.resizable(False, False)

        # create a view and place it on the root window
        view = View(self)
        view.grid(row=0, column=0, padx=10, pady=10)

        # create a model
        # model = Model('hello@pythontutorial.net')

        # create a controller
        # controller = Controller(model, view)

        # set the controller to view
        # view.set_controller(controller)