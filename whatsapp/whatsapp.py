# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:34 2022
@author: guido
"""

import time

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from whatsapp.constants import PATH_DRIVER_CHROME
from whatsapp.constants import BASE_URL
from whatsapp.constants import CHAT_LIST_CONTAINER
from whatsapp.constants import ARCHIVED_CHATS_BUTTON

class Whatsapp(webdriver.Chrome):
    
    def __init__(self, driver_path = PATH_DRIVER_CHROME):
        self.driver_path = driver_path
        super(Whatsapp, self).__init__()

    
    # Returns the list of sub-divs contained in 'recentList' main div
    def getChats(self):
        self.implicitly_wait(150)
        recentList = self.find_element(by=By.XPATH, value=CHAT_LIST_CONTAINER)
        return recentList.find_elements(by=By.XPATH, value='//span[contains(@dir,"auto")]')
        


    def landFirstPage(self):
        
        pixels = 0
        pre_height = 0
        new_height = 0
        nScrolls = 0
        
        namesBeforeScrolling = []
        namesAfterScrolling = []
        
        self.get(BASE_URL)
        self.waitForElementToAppear(60, ARCHIVED_CHATS_BUTTON)

        self.implicitly_wait(60)        
        chats = self.getChats()
        
        namesBeforeScrolling = self.fillNameList(chats)

        while True:
            nScrolls += 1
            pixels += 500
            time.sleep(0.5)
            self.execute_script('document.getElementById("pane-side").scrollTo(0,' + str(pixels) + ')')
            new_height = self.execute_script('return document.getElementById("pane-side").scrollTop')
            
            while True:

                try:
                    self.implicitly_wait(60)
                    scrolledChats = self.getChats()
                    
                    namesAfterScrolling = self.fillNameList(scrolledChats)
                    
                    self.updateList(namesBeforeScrolling, namesAfterScrolling)
                    
                    break
                        
                except:
                    self.implicitly_wait(0.1)
            
            if(pre_height < new_height):
                pre_height = self.execute_script('return document.getElementById("pane-side").scrollTop')
            else:
                break
        

    def fillNameList(self, spanList):
        nameList = []
        self.implicitly_wait(60)
        for span in spanList:
            name = span.get_attribute('title')
            if(len(name) != 0):
                nameList.append(name)
        return nameList
         
    
    def updateList(self, oldList, newList):
        for e in newList:
            if e not in oldList:
                oldList.append(e)
        
    
    def waitForElementToAppear(self, seconds, XPath):
        WebDriverWait(self, seconds).until(
            EC.presence_of_element_located((By.XPATH, XPath))
        )