# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:34 2022
@author: guido
"""

import time

from datetime import datetime

import os

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from whatsapp.constants import PATH_DRIVER_CHROME
from whatsapp.constants import BASE_URL
from whatsapp.constants import CHAT_LIST_CONTAINER
from whatsapp.constants import ARCHIVED_CHATS_BUTTON
from whatsapp.constants import CHAT_SECTION_HTML_ID
from whatsapp.constants import CHAT_MESSAGES_CONTAINERS
from whatsapp.constants import XPATH_TEXT_MESSAGES
from whatsapp.constants import XPATH_EMOJIS
from whatsapp.constants import HEADER
from whatsapp.constants import XPATH_SENDER
from whatsapp.constants import SCRAPING_DIRECTORY_NAME
from whatsapp.constants import TIMESTAMP_FORMAT

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
        for contact in contacts:
            time.sleep(1)
            name = contact.get_attribute('title')
            if(len(name) != 0):
                if(name == contactToSearch):
                    contact.click()
                    return True
                
                
                
    def fillNameList(self, spanList):
        nameList = []
        self.implicitly_wait(60)
        for span in spanList:
            name = span.get_attribute('title')
            if(len(name) != 0):
                nameList.append(name)
        return nameList
    
    
    
    def findChatToScrap(self):
        
        timestamp = self.getTimeStamp();
        os.mkdir(SCRAPING_DIRECTORY_NAME + "_" + timestamp)
        
        print("Ho creato la cartella: " + SCRAPING_DIRECTORY_NAME + "_" + timestamp)
        
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
            
            if(contactFound):
                print('Contatto trovato senza scrollare \n')
                path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                self.getConversation(path, contactName)
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
                            
                            if(contactFoundInScrolledChats):
                                print('Contatto trovato \n')
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
    
    
    
    def getConversation(self, pathToCSV, contactName):

        currentWorkingDirectory = os.getcwd()

        messagesContainers = self.find_elements(by=By.XPATH, value=CHAT_MESSAGES_CONTAINERS)
        
        for messages in messagesContainers:
            
            dataToAppend = []
            
            print('Prossimo messaggio: sono nella cartella ')
            print(currentWorkingDirectory)
            
            os.chdir(currentWorkingDirectory)
            
            finalMessage = ""
            temp = ""
            
            message = messages.find_element(
                by=By.XPATH,
                value=XPATH_TEXT_MESSAGES
            ).text
            
            emojis = messages.find_elements(
                by=By.XPATH,
                value=XPATH_EMOJIS
            )
            
            senderAndHour = messages.find_element(
                by=By.XPATH,
                value=XPATH_SENDER
            ).get_attribute("data-pre-plain-text")

            dataToAppend.append([
                self.getSender(senderAndHour),
                self.getHour(senderAndHour),
                self.getDate(senderAndHour),
                message
            ])

            self.makeCSV(dataToAppend[0], pathToCSV, contactName)
            
            if(len(emojis) != 0):
                for emoji in emojis:
                    message = message + emoji.get_attribute("data-plain-text")
                    temp += message
                finalMessage = temp
            else:
                finalMessage = message


        
    def getSender(self, senderAndHour):
        return (senderAndHour.split("] ")[1]).split(":")[0]
    
    
    
    def getHour(self, senderAndHour):
        return (senderAndHour.split("[")[1]).split(",")[0]
    
    
    
    def getDate(self, senderAndHour):
        return (senderAndHour.split(", ")[1]).split("]")[0]
    

    
    def makeCSV(self, data, pathToCSV, contactName):
        
        os.chdir(os.getcwd())
        os.chdir(pathToCSV)
        if not os.path.exists(contactName):
            os.mkdir(contactName)
        os.chdir(contactName)
        
        if not os.path.exists(contactName + ".csv"):
            newDataFrame = pd.DataFrame([data], columns=HEADER)
            newDataFrame.to_csv(contactName + ".csv", mode='a', index=False, header=True, sep=";")
        else:
            newDataFrame = pd.DataFrame([data], columns=HEADER)
            newDataFrame.to_csv(contactName + ".csv", mode='a', index=False, header=False, sep=";")
        
        
        
    def getTimeStamp(self):
        return ((datetime.now()).strftime(TIMESTAMP_FORMAT)).replace(":","")