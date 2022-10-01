# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 22:24:18 2022

@author: guido
"""

import tkinter as tk
from tkinter import ttk

class View(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # create widgets
        # label
        # self.label = ttk.Label(self, text='Email:')
        # self.label.grid(row=1, column=0)
        
        # email entry
        # self.email_var = tk.StringVar()
        # self.email_entry = ttk.Entry(self, textvariable=self.email_var, width=30)
        # self.email_entry.grid(row=1, column=1, sticky=tk.NSEW)

        # save button
        # self.save_button = ttk.Button(self, text='Save', command=self.save_button_clicked)
        # self.save_button.grid(row=1, column=3, padx=10)

        # message
        # self.message_label = ttk.Label(self, text='', foreground='red')
        # self.message_label.grid(row=2, column=1, sticky=tk.W)


    # def save_button_clicked(self):
    #     """
    #     Handle button click event
    #     :return:
    #     """
    #     if self.controller:
    #         self.controller.save(self.email_var.get())
    
    