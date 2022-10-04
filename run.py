# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 12:16:25 2022
@author: guido
"""

from whatsapp.whatsapp import Whatsapp
from configparser import ConfigParser

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

from whatsapp.constants import CURRENT_LANGUAGE
from whatsapp.constants import LANGUAGE

configurationFile = 'properties/language.ini'
config = ConfigParser()
config.read(configurationFile)

def changeLanguage(index, value, op):
    config.set(LANGUAGE, CURRENT_LANGUAGE, comboLang.get())
    with open(configurationFile, 'w') as file:
        config.write(file)
    tree.heading(0, text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['data'], anchor=tk.W)
    tree.heading(1, text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['ora'], anchor=tk.W)
    tree.heading(2, text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['mittente'], anchor=tk.W)
    tree.heading(3, text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['messaggio'], anchor=tk.W)
    output_label_2.config(text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['stato'])
    credit_label.config(text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['autore'])
    label.config(text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['opzioni'])
    choose_1.config(text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['lista_contatti'])
    choose_2.config(text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['avvio'])
    c2.config(text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['chat_archiviate'])
    choose_dest.config(text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['destinazione'])
    config.set(LANGUAGE, CURRENT_LANGUAGE, comboLang.get())
    with open(configurationFile, 'w') as file:
        config.write(file)
    return


def selectDestinationFolder():
    global destinationPath
    path = filedialog.askdirectory()
    choose_dest_label.configure(text=path)
    destinationPath = path


def uploadContactsFile():
    global pathToCSV
    filename = filedialog.askopenfilename(filetypes=(("CSV files", "*.csv*"), ("all files", "*.*")))
    choose_label.configure(text=filename)
    pathToCSV = filename
    
    
    
def openBrowser():
    Whatsapp().findChatToScrap(tree, pathToCSV, destinationPath, mediaCheckBoxValue, unarchiveChatsCheckbox)
    
    

def getMediaCheckBoxValue():
    global mediaCheckBoxValue
    mediaCheckBoxValue = save_media.get()
    
    
def getArchivedChatsCheckBoxValue():
    global unarchiveChatsCheckbox
    unarchiveChatsCheckbox = archiviate.get()



window = tk.Tk()
window.geometry("900x625")
window.title("WhatsApp Scraper")
window.grid_columnconfigure(0, weight=1)
window.resizable(False, False)
window.iconbitmap('whatsapp.ico')



tree = ttk.Treeview(window, show="headings", columns=(config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['data'], config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['ora'], config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['mittente'], config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['messaggio']), height=14)
tree.heading(0, text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['data'], anchor=tk.W)
tree.heading(1, text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['ora'], anchor=tk.W)
tree.heading(2, text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['mittente'], anchor=tk.W)
tree.heading(3, text=config[ config[LANGUAGE][CURRENT_LANGUAGE] ]['messaggio'], anchor=tk.W)
tree.column('#1', minwidth=110, stretch=False, width=110)
tree.column('#2', minwidth=90, stretch=False, width=90)
tree.column('#3', minwidth=140, stretch=False, width=140)
tree.column('#4', minwidth=535, stretch=True, width=535)
style = ttk.Style(window)
tree.grid(row=5, column=0, padx=10, pady=10, stick='W')


vsbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
vsbar.place(x=868, y=279, height=280, width=20)
tree.configure(yscrollcommand=vsbar.set)

style.theme_use("clam")
style.configure("Treeview", background="white",
                fieldbackground="white", foreground="white")
tree.bind("<Button-1>", "disableEvent")

title = tk.Label(window, text="WhatsApp Scraper", font=("Helvetica", 24))
title.grid(row=0, column=0, sticky="N", padx=20, pady=10)

output_label = tk.Label(text="Log: ")
output_label.grid(row=6, column=0, sticky="W", padx=10, pady=10)

output_label_2 = tk.Label(bg="white", fg="black", borderwidth=2, relief="groove", anchor='w')
output_label_2.configure(width=50)
output_label_2.grid(row=6, column=0, sticky="W", padx=45, pady=10)

credit_label = tk.Label(window)
credit_label.grid(row=6, column=0, stick="E", padx=10, pady=0)

xf = tk.Frame(window, relief=tk.GROOVE, borderwidth=2, width=920, height=70)
xf.grid(row=1, column=0, sticky="W", padx=10, pady=10)

label = tk.Label(xf)
label.place(relx=.06, rely=0.04, anchor=tk.W)

choose_1 = tk.Button(command=uploadContactsFile)
choose_1.grid(row=1, column=0, sticky="W", padx=30, pady=10)

xf_2 = tk.Frame(window, relief=tk.GROOVE, borderwidth=2, width=920, height=70)
xf_2.grid(row=2, column=0, sticky="W", padx=10, pady=10)

choose_dest_label = tk.Label(text="", bg="white", fg="black", borderwidth=2, relief="groove", anchor='w')
choose_dest_label.configure(width=55)
choose_dest_label.grid(row=2, column=0, sticky="W", padx=185, pady=10)

choose_dest = tk.Button(command=selectDestinationFolder)
choose_dest.grid(row=2, column=0, sticky="W", padx=30, pady=10)

choose_label = tk.Label(text="", bg="white", fg="black", borderwidth=2, relief="groove", anchor='w')
choose_label.configure(width=55)
choose_label.grid(row=1, column=0, sticky="W", padx=185, pady=10)

choose_2 = tk.Button(command=openBrowser)
choose_2.grid(row=2, column=0, sticky="E", padx=30, pady=10)

save_media = tk.IntVar()
c1 = tk.Checkbutton(window, text='Scraping media', variable=save_media, onvalue=1, offvalue=0, command=getMediaCheckBoxValue)
c1.grid(row=1, column=0, stick="E", padx=200, pady=10)

archiviate = tk.IntVar()
c2 = tk.Checkbutton(window, variable=archiviate, onvalue=1, offvalue=0, command=getArchivedChatsCheckBoxValue)
c2.grid(row=1, column=0, stick="E", padx=30, pady=10)

v = tk.StringVar()
v.trace('w', changeLanguage)
comboLang = ttk.Combobox(window, textvar=v, state="readonly",
                         values=[
                             "English",
                             "Italiano",
                             "Francais",
                             "Deutsch"])
comboLang.grid(row=0, column=0, sticky="W", padx=10, pady=10)
comboLang.set(config[LANGUAGE][CURRENT_LANGUAGE])

window.mainloop()