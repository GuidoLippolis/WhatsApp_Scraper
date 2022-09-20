# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:34 2022
@author: guido
"""

import collections

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
from whatsapp.constants import XPATH_TEXT_MESSAGES_CONTAINERS
from whatsapp.constants import XPATH_EMOJIS
from whatsapp.constants import HEADER
from whatsapp.constants import XPATH_SENDER
from whatsapp.constants import XPATH_TEXT_MESSAGES
from whatsapp.constants import SCRAPING_DIRECTORY_NAME
from whatsapp.constants import TIMESTAMP_FORMAT
from whatsapp.constants import DIRECTORY_CALLBACK
from whatsapp.constants import PIXELS_TO_SCROLL
from whatsapp.constants import VIDEO_PLAY_BUTTON_XPATH
from whatsapp.constants import VIDEO_DOWNLOAD_BUTTON_XPATH
from whatsapp.constants import CLOSE_BUTTON_MEDIA_XPATH
from whatsapp.constants import MESSAGE_METADATA_FORMAT

import pandas as pd

from selenium.common.exceptions import ElementNotVisibleException

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
            if(len(name) != 0 and name == contactToSearch):
                    contact.click()
                    # self.wait(25)
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
                    updatedList = []
                    nScrolls += 1
                    print('Scroll n. ' + str(nScrolls) + '... \n')
                    pixels += PIXELS_TO_SCROLL
                    self.execute_script('document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTo(0,' + str(pixels) + ')')
                    new_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
                    
                    while True:
                        try:
                            self.implicitly_wait(200)
                            time.sleep(1)
                            scrolledChats = self.getContacts()
                            
                            updatedList = self.updateList(chats, scrolledChats)
                            
                            scrolledChatsAsStrings = self.fillNameList(updatedList)
                            
                            print('Dopo lo scroll n.' + str(nScrolls) + ' ci sono: \n')
                            print(scrolledChatsAsStrings)
                    
                            contactFoundInScrolledChats = self.searchContactToClick(updatedList, contactName)
                            
                            print('Contact found = ' + str(contactFoundInScrolledChats))
                            
                            if(contactFoundInScrolledChats):
                                print('Contatto trovato allo scroll n. ' + str(nScrolls) + '\n')
                                path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                                self.getConversation(path, contactName)
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
                    
                if(endOfSearch):
                    path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                    self.getConversation(path, contactName)
                    

                    
    def readContactsFromFile(self, pathToFile):
        contacts = pd.read_csv(pathToFile)
        return contacts['Nome'].values
    
    
    
    def getConversation(self, pathToCSV, contactName):
        
        downloadMedia = False

        messageMetadataList = []
        
        messages = self.find_elements(by=By.XPATH, value=XPATH_TEXT_MESSAGES_CONTAINERS)
        
        textMessages = self.find_elements(by=By.XPATH, value=XPATH_TEXT_MESSAGES)
        
        print('Found ' + str(len(messages)) + ' text messages... \n')
        
        # Getting messages along with metadata
        for message in messages:
            metadata = message.find_element(
                by=By.XPATH,
                value=XPATH_SENDER
            ).get_attribute("data-pre-plain-text")
            messageMetadataList.append(metadata)

            emojis = message.find_elements(
                by=By.XPATH,
                value=XPATH_EMOJIS
            )
            
            if(len(emojis)):
                print('Getting emojis...')
                for emoji in emojis:
                    print(emoji.get_attribute('alt'))
                                        
            
        sortedMetadataDict = self.sortMetadataByTime(messageMetadataList, textMessages)
        
        print(sortedMetadataDict)

        for row in sortedMetadataDict:
            os.chdir(DIRECTORY_CALLBACK)
            dataToAppend = []
            dataToAppend.append([
                # Date
                (row[0].strftime(MESSAGE_METADATA_FORMAT)).split(" ")[0],
                # Hour
                (row[0].strftime(MESSAGE_METADATA_FORMAT)).split(" ")[1],
                # Sender
                row[1],
                # Message
                row[2]
            ])
            self.makeCSV(dataToAppend[0], pathToCSV, contactName)
            
        if(downloadMedia):
            self.downloadMedia()


        
    def sortMetadataByTime(self, messageMetadataList, textMessages):
        
        metadataDict = []
        finalDict = []
        
        for metadata in messageMetadataList:
            timeStr = self.getDateAsString(metadata) + ' ' + self.getHourAsString(metadata)
            timeObj = datetime.strptime(timeStr, MESSAGE_METADATA_FORMAT)
            sender = self.getSender(metadata)
            metadataDict.append((timeObj, sender))
            
        sortedMetadataDict = sorted(metadataDict, key = lambda x: x[0])
        
        for sortedMetadata, textMessage in zip(sortedMetadataDict, textMessages):
            sortedMetadata = sortedMetadata + (textMessage.get_dom_attribute('innerText'), )
            finalDict.append(sortedMetadata)
            
        return finalDict
            
    
    
    def downloadMedia(self):
        
            videoPlayers = self.find_elements(by=By.XPATH, value=VIDEO_PLAY_BUTTON_XPATH)
            
            print(str(len(videoPlayers)) + ' video(s) found... \n')
            
            countVideo = 0
            
            for playButton in videoPlayers:
                
                countVideo += 1
                
                print('Looking for video n. ' + str(countVideo) + '... \n')
                print(playButton)
                
                playButton.click()
                
                WebDriverWait(self, 60).until(
                    EC.presence_of_element_located((By.XPATH, VIDEO_DOWNLOAD_BUTTON_XPATH))
                )
                
                downloadButton = self.find_element(by=By.XPATH, value=VIDEO_DOWNLOAD_BUTTON_XPATH)
                
                downloadButton.click()
                
                print('Downloaded! \n')
                
                WebDriverWait(self, 60).until(
                    EC.presence_of_element_located((By.XPATH, CLOSE_BUTTON_MEDIA_XPATH))
                )
                
                closeButton = self.find_element(by=By.XPATH, value=CLOSE_BUTTON_MEDIA_XPATH)
                
                closeButton.click()
    
    
    
    def makeCSV(self, data, pathToCSV, contactName):
        
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
        
        
        
    def getSender(self, messageMetadata):
        return (messageMetadata.split("] ")[1]).split(":")[0]
    
    
    
    def getHourAsString(self, messageMetadata):
        return (messageMetadata.split("[")[1]).split(",")[0]
    
    
    
    def getDateAsString(self, messageMetadata):
        return (messageMetadata.split(", ")[1]).split("]")[0]  
        
    
    
    def getTimeStamp(self):
        return ((datetime.now()).strftime(TIMESTAMP_FORMAT)).replace(":","")
    
    
    
    def updateList(self, firstList, secondList):
        updatedList = []
        for e in secondList:
            if e not in firstList:
                updatedList.append(e)
        return updatedList