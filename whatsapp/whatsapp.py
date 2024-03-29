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

import pandas as pd

class Whatsapp(webdriver.Chrome):
    
    def __init__(self, driver_path = PATH_DRIVER_CHROME):
        self.driver_path = driver_path
        super(Whatsapp, self).__init__()
        
        
        
    def getContacts(self):
        self.implicitly_wait(150)
        recentList = self.find_element(by=By.XPATH, value=CHAT_LIST_CONTAINER)
        return recentList.find_elements(by=By.XPATH, value='//span[contains(@dir,"auto")]')
    
    
    
    def waitForElementToAppear(self, seconds, XPath):
        WebDriverWait(self, seconds).until(
            EC.presence_of_element_located((By.XPATH, XPath))
        )
        
        
        
    def searchContactToClick(self, contacts, contactToSearch):
        
        print('Sono in searchContactToClick \n')
        print('Devo cercare tra ' + str(len(contacts)) + ' contatti se è presente ' + contactToSearch)
        
        count = 0
        
        for contact in contacts:
            name = contact.get_attribute('title')
            if(len(name) != 0):
                count += 1
                print('Confronto con il contatto n. ' + str(count) + '\n')
                print('Contact = ' + name)
                if(name == contactToSearch):
                    print('TROVATO! \n')
                    contact.click()
                    return True
                
        # for contact in contacts:
            
        #     time.sleep(5)
            
        #     name = contact.get_attribute('title')
            
        #     print('Contact: ' + name)
        #     print('\n')
        #     print('Contact to search: ' + contactToSearch)
            
        #     # if(len(name) != 0):
        #     if(name == contactToSearch):
        #         print('TROVATO!!! \n')
        #         contact.click()
        #         return True
        #     else:
        #         return False
                
                
                
    def fillNameList(self, spanList):
        nameList = []
        self.implicitly_wait(60)
        for span in spanList:
            name = span.get_attribute('title')
            if(len(name) != 0):
                nameList.append(name)
        return nameList
    
    
    
    def findChatToScrap(self):
        
        endOfSearch = False
        
        pixels = 0
        pre_height = 0
        new_height = 0
        nScrolls = 0
        
        self.get(BASE_URL)
        self.waitForElementToAppear(500, ARCHIVED_CHATS_BUTTON)
        
        time.sleep(1)
        chats = self.getContacts()
        
        print('Prima di scrollare erano presenti: \n')
        chatsAsStrings = self.fillNameList(chats)
        print(chatsAsStrings)
        
        contactNamesFromCSV = self.readContactsFromFile('./contatti.csv')
        
        for contactName in contactNamesFromCSV:
            
            print('Cercando ' + contactName + '... \n')
            
            contactFound = self.searchContactToClick(chats, contactName)
            
            if(contactFound == True):
                print('Contatto trovato senza scrollare \n')
            else:
                
                while True:
                    nScrolls += 1
                    print('Scroll n. ' + str(nScrolls) + '... \n')
                    pixels += 500
                    self.execute_script('document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTo(0,' + str(pixels) + ')')
                    new_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
                    
                    while True:
                        try:
                            self.implicitly_wait(200)
                            time.sleep(1)
                            scrolledChats = self.getContacts()
                            
                            scrolledChatsAsStrings = self.fillNameList(scrolledChats)
                            
                            print('Dopo lo scroll n.' + str(nScrolls) + ' ci sono: \n')
                            print(scrolledChatsAsStrings)
                    
                            contactFoundInScrolledChats = self.searchContactToClick(scrolledChats, contactName)
                            
                            print('Contact found = ' + str(contactFoundInScrolledChats))
                            
                            if(contactFoundInScrolledChats == True):
                                print('Contatto trovato  allo scroll n. ' + str(nScrolls) + '\n')
                                endOfSearch = True
                                break
                            
                            break
                        except:
                            self.implicitly_wait(0.5)
                            
                    if(endOfSearch):
                        break
                    
                    if(pre_height < new_height):
                        pre_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
                    else:
                        break
                    
                    
                    
    def readContactsFromFile(self, pathToFile):
        contacts = pd.read_csv(pathToFile)
        return contacts['Nome'].values