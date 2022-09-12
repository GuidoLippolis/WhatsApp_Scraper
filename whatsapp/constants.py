# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:48 2022

@author: guido
"""

PATH_DRIVER_CHROME = "C:/GitHub_Repositories/WhatsApp_Scraper/drivers"
BASE_URL = "https://web.whatsapp.com/"

# Contenitore principale delle chat aperte nella home
CHAT_LIST_CONTAINER = '//*[@id="pane-side"]/div[2]/div/div'

# Contenitore della chat
CHAT_MESSAGES_CONTAINER = '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div[2]/div[3]'


ARCHIVED_CHATS_BUTTON = '//*[@id="pane-side"]/button/div/div[2]/div/div'
CHAT_SECTION_HTML_ID = 'pane-side'