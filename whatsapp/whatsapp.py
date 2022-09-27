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
from whatsapp.constants import XPATH_RECENT_CHATS
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
from whatsapp.constants import DOWNLOAD_BUTTON_XPATH
from whatsapp.constants import CLOSE_BUTTON_MEDIA_XPATH
from whatsapp.constants import MESSAGE_METADATA_FORMAT
from whatsapp.constants import XPATH_IMAGES
from whatsapp.constants import XPATH_AUDIOS
from whatsapp.constants import XPATH_DROP_DOWN_MENU_DOWNLOAD_AUDIOS
from whatsapp.constants import XPATH_DOWNLOAD_AUDIOS
from whatsapp.constants import XPATH_ARCHIVED_CHATS
from whatsapp.constants import XPATH_DROP_DOWN_MENU_ARCHIVED_CHATS
from whatsapp.constants import XPATH_UNARCHIVE_BUTTON

import pandas as pd

from selenium.webdriver import ActionChains

class Whatsapp(webdriver.Chrome):
    
    def __init__(self, driver_path = PATH_DRIVER_CHROME):
        self.driver_path = driver_path
        super(Whatsapp, self).__init__()
        
        
        
    def getContacts(self):
        self.implicitly_wait(150)
        recentList = self.find_element(by=By.XPATH, value=CHAT_LIST_CONTAINER)
        return recentList.find_elements(by=By.XPATH, value=XPATH_RECENT_CHATS)
    
    
    
    def waitForElementToAppear(self, seconds, XPath):
        WebDriverWait(self, seconds).until(
            EC.presence_of_element_located((By.XPATH, XPath))
        )
        
        
        
    def searchContactToClick(self, contacts, contactToSearch):
        
        for contact in contacts:
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
    
    
    
    def testArchivedChats(self):
        
        self.get(BASE_URL)
        self.waitForElementToAppear(500, ARCHIVED_CHATS_BUTTON)
        
        archivedChatsButton = self.find_element(by=By.XPATH, value=ARCHIVED_CHATS_BUTTON)
        archivedChatsButton.click()
        
        unarchivedContacts = []
        
        self.wait(15)
        
        archivedChats = self.find_elements(by=By.XPATH, value=XPATH_ARCHIVED_CHATS)
        
        archivedChats2 = []
        
        for a in archivedChats:
            if(len(a.get_attribute('title')) != 0):
                archivedChats2.append(a)

        for chat in archivedChats2:
            print('Stampo il nome della chat \n')
            if(chat.is_displayed()):
                unarchivedContacts.append(chat.get_attribute('title'))
                print('Unarchiving contact ' + chat.get_attribute('title') + '... \n')
                self.wait(5)
                a = ActionChains(self)
                print('a.move_to_element(chat).perform() \n')
                a.move_to_element(chat).perform()
                self.wait(1)
                print('Recupero il bottone drop down \n')
                dropDownArchivedChatButton = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_ARCHIVED_CHATS)
                dropDownArchivedChatButton.click()
                self.wait(1)
                print('Recupero il bottone unarchive \n')
                unarchiveButton = self.find_element(by=By.XPATH, value=XPATH_UNARCHIVE_BUTTON)
                unarchiveButton.click()
        

    
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
            if(contactFound == True):
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
                            
                            if(contactFoundInScrolledChats == True):
                                print('Contatto trovato allo scroll n. ' + str(nScrolls) + '\n')
                                endOfSearch = True
                                path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                                self.getConversation(path, contactName)
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
        
        print('Getting conversation with ' + contactName + '... \n')
        
        messageMetadataList = []
        
        # Retrieving all divs containing text messages
        messages = self.find_elements(by=By.XPATH, value=XPATH_TEXT_MESSAGES_CONTAINERS)
        
        # Retrieving text messages
        textMessages = self.find_elements(by=By.XPATH, value=XPATH_TEXT_MESSAGES)
        
        for message in messages:
            
            WebDriverWait(self, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, ".//div[contains(@title,'message-')]")
                )    
            )
            
            # Getting metadata for every message (sender, date and hour)
            metadata = message.find_element(
                by=By.XPATH,    
                value=XPATH_SENDER
            ).get_attribute("data-pre-plain-text")
            
            messageMetadataList.append(metadata)

        # Messages are sorted in descending order (if the last attribute is set to "True")
        sortedMetadataDict = self.sortMessagesByTime(messageMetadataList, textMessages, True)
            
        for row in sortedMetadataDict:
                # Getting back to the main directory
            os.chdir(DIRECTORY_CALLBACK)
                # Filling a list where data to be written in the .csv file are passed as input
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
                # A .csv file named as the contact name the scraper is processing is created
            self.makeCSV(dataToAppend[0], pathToCSV, contactName)
            

    
    def sortMessagesByTime(self, messageMetadataList, textMessages, reverse):
        
        metadataDict = []
        finalDict = []
        
        for metadata in messageMetadataList:
            timeStr = self.getDateAsString(metadata) + ' ' + self.getHourAsString(metadata)
            timeObj = datetime.strptime(timeStr, MESSAGE_METADATA_FORMAT)
            sender = self.getSender(metadata)
            metadataDict.append((timeObj, sender))
        
        if(reverse == True):
            
            textMessages.reverse()
            sortedMetadataDict = sorted(metadataDict, key = lambda x: x[0], reverse=reverse)
            
            for sortedMetadata, textMessage in zip(sortedMetadataDict, textMessages):
                sortedMetadata = sortedMetadata + (textMessage.get_dom_attribute('innerText'), )
                finalDict.append(sortedMetadata)
        else:
            
            for sortedMetadata, textMessage in zip(metadataDict, textMessages):
                sortedMetadata = sortedMetadata + (textMessage.get_dom_attribute('innerText'), )
                finalDict.append(sortedMetadata)
            
        return finalDict
     


    def downloadAudios(self):
        
        audios = self.find_elements(by=By.XPATH, value=XPATH_AUDIOS)
        
        for audio in audios:
            
            ActionChains(self).move_to_element(audio).perform()
            
            dropDownMenu = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_DOWNLOAD_AUDIOS)
            
            dropDownMenu.click()
            
            self.wait(3)
            
            downloadButton = self.find_element(by=By.XPATH, value=XPATH_DOWNLOAD_AUDIOS)
            
            downloadButton.click()
            
            self.wait(3)
        


    def downloadImages(self):
        
        images = self.find_elements(by=By.XPATH, value=XPATH_IMAGES)
        
        for image in images:
            
            image.click()
            
            self.wait(3)
            
            downloadButton = self.find_element(by=By.XPATH, value=DOWNLOAD_BUTTON_XPATH)
            
            downloadButton.click()
            
            self.wait(3)
            
            closeButton = self.find_element(by=By.XPATH, value=CLOSE_BUTTON_MEDIA_XPATH)
            
            closeButton.click()
        
    
    
    def downloadVideos(self):
        
        videoPlayers = self.find_elements(by=By.XPATH, value=VIDEO_PLAY_BUTTON_XPATH)
        
        for playButton in videoPlayers:
            
            playButton.click()
            
            self.wait(5)
            
            downloadButton = self.find_element(by=By.XPATH, value=DOWNLOAD_BUTTON_XPATH)
            
            downloadButton.click()
            
            self.wait(3)
            
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
    
    
    
    def wait(self, seconds):
        for i in range(1, seconds+1):
            time.sleep(1)
            print(str(i) + '... \n')