# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:48 2022

@author: guido
"""

PATH_DRIVER_CHROME = "C:/GitHub_Repositories/WhatsApp_Scraper/drivers"
BASE_URL = "https://web.whatsapp.com/"

# Container of all open chats in the home page
CHAT_LIST_CONTAINER = '//*[@id="pane-side"]/div[2]/div/div'

# HTML id value of CHAT_MESSAGES_CONTAINER
CHAT_SECTION_HTML_ID = 'pane-side'

# XPath for recent chats in recent list
XPATH_RECENT_CHATS = '//span[contains(@dir,"auto")]'

# Button to get archived chats
ARCHIVED_CHATS_BUTTON = '//*[@id="pane-side"]/button/div/div[2]/div/div'

# XPath for querying text messages containers without emojis and with metadata (hour, date and sender)
XPATH_TEXT_MESSAGES_CONTAINERS = "//div[contains(@data-testid,'msg-container') and contains(@class,'_1-lf9 _3mSPV')]"

# XPath for querying text messages without emojis
XPATH_TEXT_MESSAGES = "//span[contains(@class,'i0jNr selectable-text copyable-text') and contains(@dir,'ltr')]"

# XPath for querying emojis
XPATH_EMOJIS = "//img[contains(@class,'selectable-text copyable-text')]"

# XPath of message sender
XPATH_SENDER = ".//div[contains(@data-pre-plain-text,'[')]"

# Header of CSV file containing scraped messages
HEADER = ["Data", "Ora", "Mittente", "Messaggio"]

# Name of the directory containing scraped chats
SCRAPING_DIRECTORY_NAME = "Scraped"

# Timestamp format for directory names
TIMESTAMP_FORMAT = "%H:%M:%S%f"

# Folder to go back for every message
DIRECTORY_CALLBACK = "C:\GitHub_Repositories\WhatsApp_Scraper"

# Number of pixels to scroll
PIXELS_TO_SCROLL = 1000

# XPath identifier for video play button
VIDEO_PLAY_BUTTON_XPATH = "//div//span[contains(@data-testid,'media-play')]"

# XPath identifier for video download button
DOWNLOAD_BUTTON_XPATH = "//span[contains(@data-testid, 'download')]"

# XPath identifier for close button (after opening a media)
CLOSE_BUTTON_MEDIA_XPATH = "//span[contains(@data-testid, 'x-viewer')]"

# Format for message metadata
MESSAGE_METADATA_FORMAT = '%d/%m/%Y %H:%M'

# XPath for image tags
XPATH_IMAGES = "//div[contains(@data-testid,'image-thumb')]"

# XPath for audio play buttons
XPATH_AUDIOS = "//span[contains(@data-testid, 'audio-play')]"

# XPath for drop down menu for downloading audios
XPATH_DROP_DOWN_MENU_DOWNLOAD_AUDIOS = "//span[contains(@data-testid, 'down-context')]"

# XPath for downloading audios
XPATH_DOWNLOAD_AUDIOS = "//span//li[contains(@data-testid, 'mi-msg-download')]"

# Path to Downloads folder in Windows
DOWNLOADS_PATH = "C://Users//guido//Downloads"

# XPath archived chats
XPATH_ARCHIVED_CHATS = '//div[contains(@class,"_3uIPm WYyr1") and not(contains(@aria-label,"Lista"))]//span[contains(@dir,"auto")]'

# XPath drop down menu for archived chats
XPATH_DROP_DOWN_MENU_ARCHIVED_CHATS = '//button//span[contains(@data-testid,"down")]'

# XPath unarchive button
XPATH_UNARCHIVE_BUTTON = '//li[contains(@data-testid, "mi-archive")]'