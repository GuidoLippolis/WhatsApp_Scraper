# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:48 2022

@author: guido
"""

PATH_DRIVER_CHROME = "C:/GitHub_Repositories/WhatsApp_Scraper/drivers"
BASE_URL = "https://web.whatsapp.com/"

# Container of all open chats in the home page
CHAT_LIST_CONTAINER = '//*[@id="pane-side"]/div[2]/div/div'

# Containers of all messages of a single chat
CHAT_MESSAGES_CONTAINERS = "//div[contains(@class,'message-')]"

# HTML id value of CHAT_MESSAGES_CONTAINER
CHAT_SECTION_HTML_ID = 'pane-side'

# Button to get archived chats
ARCHIVED_CHATS_BUTTON = '//*[@id="pane-side"]/button/div/div[2]/div/div'

# XPath for querying text messages without emojis
XPATH_TEXT_MESSAGES = ".//span[contains(@class,'selectable-text copyable-text')]"

# XPath for querying emojis
XPATH_EMOJIS = ".//img[contains(@class,'selectable-text copyable-text')]"

# XPath of message sender
XPATH_SENDER = ".//div[contains(@data-pre-plain-text,'[')]"

# Header of CSV file containing scraped messages
HEADER = ["Mittente", "Messaggio", "Orario"]