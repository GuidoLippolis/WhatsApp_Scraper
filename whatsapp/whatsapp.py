# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:34 2022

@author: guido
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from whatsapp.constants import PATH_DRIVER_CHROME
from whatsapp.constants import BASE_URL

class Whatsapp(webdriver.Chrome):
    
    def __init__(self, driver_path = PATH_DRIVER_CHROME):
        self.driver_path = driver_path
        super(Whatsapp, self).__init__()
    
    
    # Returns the list of sub-divs contained in 'recentList' main div
    def getChats(self):
        self.implicitly_wait(150)
        recentList = self.find_element(by=By.XPATH, value='//*[@id="pane-side"]/div[2]/div/div')
        return recentList.find_elements(by=By.XPATH, value='//span[contains(@dir,"auto")]')
            
        
        
    def landFirstPage(self):
        nPixels = 500
        chatLabels = []
        chatNames = []
        self.get(BASE_URL)
        self.implicitly_wait(150)
        
        # List containing WebElements associated to
        # single contacts before the page is scrolled down
        chatsBeforeScrolling = self.getChats()
        
        for chat in chatsBeforeScrolling:
            # Every contact's name is appended to the name list to be returned
            chatNames.append(chat.get_attribute('title'))
        
        print(chatNames)
        
        for contactName in chatsBeforeScrolling:
            chatLabels.append(contactName)
        
        
        for chat in chatsBeforeScrolling:
            self.execute_script("window.scrollBy(0,"+ str(nPixels) +");")
            # self.execute_script("arguments[0].scrollBy(0,500)", "")
            self.implicitly_wait(150)
            recentList_scrolled = self.getChats()
         
         
        for list_scrolled in recentList_scrolled:
            chatLabels.append(list_scrolled)
            chatNames.append(list_scrolled.get_attribute('title'))
        
        
        print(chatNames)
        print('\n')
        print(len(chatNames))