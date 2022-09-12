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
from whatsapp.constants import CHAT_SECTION_HTML_ID
from whatsapp.constants import CHAT_MESSAGES_CONTAINER

class Whatsapp(webdriver.Chrome):
    
    def __init__(self, driver_path = PATH_DRIVER_CHROME):
        self.driver_path = driver_path
        super(Whatsapp, self).__init__()

    
    # Returns the list of <span> tags contained in 'recentList' main div
    def getContacts(self):
        self.implicitly_wait(150)
        recentList = self.find_element(by=By.XPATH, value=CHAT_LIST_CONTAINER)
        return recentList.find_elements(by=By.XPATH, value='//span[contains(@dir,"auto")]')
        
    # Stops the program for the given number of seconds
    def wait(self, seconds):
        for i in range(0,seconds):
            # print(str(i) + '... \n')
            time.sleep(1)


    # Opens the browser and does all the rest
    def landFirstPage(self):
        
        pixels = 0
        pre_height = 0
        new_height = 0
        
        namesBeforeScrolling = []
        namesAfterScrolling = []
        
        self.get(BASE_URL)
        self.waitForElementToAppear(500, ARCHIVED_CHATS_BUTTON)

        self.wait(5)

        chats = self.getContacts()
        
        namesBeforeScrolling = self.fillNameList(chats)
        
        while True:
            pixels += 500
            time.sleep(0.5)
            self.execute_script('document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTo(0,' + str(pixels) + ')')
            new_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
            
            while True:

                try:
                    self.implicitly_wait(200)
                    scrolledChats = self.getContacts()
                    
                    namesAfterScrolling = self.fillNameList(scrolledChats)
                    
                    self.updateList(namesBeforeScrolling, namesAfterScrolling)
                    
                    break
                        
                except:
                    self.implicitly_wait(0.5)
            
            if(pre_height < new_height):
                pre_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
            else:
                break
        print(namesBeforeScrolling)



    def fillNameList(self, spanList):
        nameList = []
        self.implicitly_wait(200)
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
        
    
    def searchContactToClick(self, contacts, contactToSearch):
        for contact in contacts:
            self.wait(2)
            name = contact.get_attribute('title')
            if(len(name) != 0):
                if(name == contactToSearch):
                    contact.click()
                    return True
    
        
    def getChatOfContact(self):
        contactName = 'Cosimo Gennaro'
        
        pixels = 0
        pre_height = 0
        new_height = 0           
        
        self.get(BASE_URL)
        self.waitForElementToAppear(500, ARCHIVED_CHATS_BUTTON)
        
        self.wait(5)
        chats = self.getContacts()
        
        contactFound = self.searchContactToClick(chats, contactName)
        
        if(contactFound == True):
            print('Contatto trovato senza scrollare \n')
        
        endAll = False
        
        if(contactFound == False):
            while True:
                pixels += 500
                time.sleep(0.5)
                self.execute_script('document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTo(0,' + str(pixels) + ')')
                new_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
            
                while True:
    
                    try:
                        self.implicitly_wait(200)
                        self.wait(5)
                        scrolledChats = self.getContacts()
                        
                        contactFoundInScrolledChats = self.searchContactToClick(scrolledChats, contactName)
                        
                        if(contactFoundInScrolledChats):
                            print('Contatto trovato \n')
                            endAll = True
                            break
                        
                        namesAfterScrolling = self.fillNameList(scrolledChats)
                        
                        break
                            
                    except:
                        self.implicitly_wait(0.5)
            
                if(endAll):
                    break
            
                if(pre_height < new_height):
                    pre_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
                else:
                    break
        
        