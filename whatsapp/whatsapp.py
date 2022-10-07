# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:34 2022
@author: guido
"""

import logging
logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

from configparser import ConfigParser

import time
from datetime import datetime
import os
import re
import pathlib
import shutil
import zipfile
import hashlib
import tkinter as tk
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from whatsapp.constants import PATH_DRIVER_CHROME
from whatsapp.constants import BASE_URL
from whatsapp.constants import CHAT_LIST_CONTAINER
from whatsapp.constants import XPATH_RECENT_CHATS
from whatsapp.constants import ARCHIVED_CHATS_BUTTON
from whatsapp.constants import CHAT_SECTION_HTML_ID
from whatsapp.constants import XPATH_TEXT_MESSAGES_CONTAINERS
from whatsapp.constants import XPATH_EMOJIS
from whatsapp.constants import HEADER
from whatsapp.constants import HEADER_HASHING
from whatsapp.constants import XPATH_SENDER
from whatsapp.constants import XPATH_TEXT_MESSAGES
from whatsapp.constants import SCRAPING_DIRECTORY_NAME
from whatsapp.constants import TIMESTAMP_FORMAT
from whatsapp.constants import DIRECTORY_CALLBACK
from whatsapp.constants import PATHS
from whatsapp.constants import PIXELS_TO_SCROLL
from whatsapp.constants import VIDEO_PLAY_BUTTON_XPATH
from whatsapp.constants import DOWNLOAD_BUTTON_XPATH
from whatsapp.constants import CLOSE_BUTTON_MEDIA_XPATH
from whatsapp.constants import MESSAGE_METADATA_FORMAT
from whatsapp.constants import XPATH_IMAGES
from whatsapp.constants import XPATH_AUDIOS
from whatsapp.constants import XPATH_GIFS
from whatsapp.constants import XPATH_DROP_DOWN_MENU_DOWNLOAD_AUDIOS
from whatsapp.constants import XPATH_DOWNLOAD_AUDIOS
from whatsapp.constants import XPATH_ARCHIVED_CHATS
from whatsapp.constants import XPATH_DROP_DOWN_MENU_ARCHIVED_CHATS
from whatsapp.constants import XPATH_UNARCHIVE_BUTTON
from whatsapp.constants import DOWNLOADS_PATH
from whatsapp.constants import XPATH_DOC_LIST
from whatsapp.constants import ACCEPTED_EXTENSIONS
from whatsapp.constants import XPATH_CHAT_FILTER_BUTTON
from whatsapp.constants import MULTIMEDIA_ZIP_NAME
from whatsapp.constants import HASHING_CSV_FILE_NAME
from whatsapp.constants import CLOSE_ARCHIVED_CHATS_SECTION
from whatsapp.constants import CHARACTERS_TO_AVOID
from whatsapp.constants import REGULAR_EXPRESSION

from whatsapp.exceptions.ImageNotFoundException import ImageNotFoundException
from whatsapp.exceptions.VideoNotFoundException import VideoNotFoundException
from whatsapp.exceptions.AudioNotFoundException import AudioNotFoundException
from whatsapp.exceptions.DocumentNotFoundException import DocumentNotFoundException
from whatsapp.exceptions.ArchivedChatsButtonNotFoundException import ArchivedChatsButtonNotFoundException
from whatsapp.exceptions.NoMessagesException import NoMessagesException

class Whatsapp(webdriver.Chrome):
    
    def __init__(self, driver_path = PATH_DRIVER_CHROME):
        self.driver_path = driver_path
        super(Whatsapp, self).__init__()
      
    
    
    def getParser(self):
        paths_file = 'paths.ini'
        paths_parser = ConfigParser()
        paths_parser.read(paths_file)
        return paths_parser
    
    
        
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
            if(len(name) != 0 and name == contactToSearch):
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
    
    
    
    def unarchiveChats(self):
        
        try:
            
            archivedChatsButton = self.find_elements(by=By.XPATH, value=ARCHIVED_CHATS_BUTTON)
            
            if(len(archivedChatsButton) == 0):
                logging.error("IL BOTTONE DELLE CHAT ARCHIVIATE NON E' PRESENTE")
                raise ArchivedChatsButtonNotFoundException("IL BOTTONE DELLE CHAT ARCHIVIATE NON E' PRESENTE! \n")
            else:
                time.sleep(5)
                self.waitForElementToAppear(500, ARCHIVED_CHATS_BUTTON)
                
                archivedChatsButton[0].click()
                
                time.sleep(5)
        
                unarchivedContacts = []
                archivedChats2 = []
                    
                archivedChats = self.find_elements(by=By.XPATH, value=XPATH_ARCHIVED_CHATS)
                
                for a in archivedChats:
                    if(len(a.get_attribute('title')) != 0):
                        archivedChats2.append(a)
        
                for chat in archivedChats2:
                    if(chat.is_displayed()):
                        unarchivedContacts.append(chat.get_attribute('title'))
                        time.sleep(2)
                        ActionChains(self).move_to_element(chat).perform()
                        time.sleep(1)
                        dropDownArchivedChatButton = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_ARCHIVED_CHATS)
                        dropDownArchivedChatButton.click()
                        time.sleep(1)
                        unarchiveButton = self.find_element(by=By.XPATH, value=XPATH_UNARCHIVE_BUTTON)
                        unarchiveButton.click()
                        time.sleep(5)
                
                closeArchivedChatsSectionButton = self.find_element(by=By.XPATH, value=CLOSE_ARCHIVED_CHATS_SECTION)
                closeArchivedChatsSectionButton.click()
                
                return unarchivedContacts
            
        except ArchivedChatsButtonNotFoundException as acb:
            print(acb)
          


    def getAllChatsDefault(self, timestamp, downloadMediaCheckbox, tree, destinationPath, statesDict, output, paths_parser):
        
        pixels = 0
        pre_height = 0
        new_height = 0
        nScrolls = 0
        
        endOfSearch = False
        
        chats = self.getContacts()
        
        for chat in chats:
            contactName = chat.get_attribute('title')
            if(len(contactName) != 0):
                
                path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                contactFound = self.searchContactToClick(chats, contactName)
                if(contactFound == True):
                    # Al metodo getConversation() passo il percorso /SCRAPED_timestamp/
                    self.getConversation(path, contactName, tree)
                
                    if(downloadMediaCheckbox == 1):
                        # Torno nella cartella ../Output/
                        os.chdir(destinationPath)
                        self.downloadMedia(statesDict, output)
                        # Una volta scaricati i file, li metto nella cartella ../Output/SCRAPED_timestamp/nome_contatto/
                        self.moveFilesToMainDirectory(destinationPath + "\\" + path + "\\" + contactName, paths_parser)
                        # I file vengono zippati nella stessa cartella
                        self.zipFiles(destinationPath + "\\" + path + "\\" + contactName, contactName)
                        self.zipHasher(destinationPath + "\\" + path + "\\" + contactName)
                        # os.chdir(r'C:\GitHub_Repositories\WhatsApp_Scraper')
                
        
        while True:
            updatedList = []
            nScrolls += 1
            pixels += PIXELS_TO_SCROLL
            self.execute_script('document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTo(0,' + str(pixels) + ')')
            new_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
            
            while True:
                
                try:
                    self.implicitly_wait(200)
                    scrolledChats = self.getContacts()
                    updatedList = self.updateList(chats, scrolledChats)
                    
                    for scrolledChat in updatedList:
                        contactName = scrolledChat.get_attribute('title')
                        if(len(contactName) != 0):
                            path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                            contactFound = self.searchContactToClick(scrolledChats, contactName)
                            if(contactFound == True):
                                # Al metodo getConversation() passo il percorso /SCRAPED_timestamp/
                                self.getConversation(path, contactName, tree)
                    
                                if(downloadMediaCheckbox == 1):
                                    # Torno nella cartella ../Output/
                                    os.chdir(destinationPath)
                                    self.downloadMedia(statesDict, output)
                                    # Una volta scaricati i file, li metto nella cartella ../Output/SCRAPED_timestamp/nome_contatto/
                                    self.moveFilesToMainDirectory(destinationPath + "\\" + path + "\\" + contactName, paths_parser)
                                    # I file vengono zippati nella stessa cartella
                                    self.zipFiles(destinationPath + "\\" + path + "\\" + contactName, contactName)
                                    self.zipHasher(destinationPath + "\\" + path + "\\" + contactName)
                                    # os.chdir(r'C:\GitHub_Repositories\WhatsApp_Scraper')
                    
                            break
                    break
                except:
                    self.implicitly_wait(0.5)
                    
            if(endOfSearch == True):
                break
            
            if(pre_height < new_height):
                pre_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
            else:
                break
    

    
    def findChatToScrap(self, tree, pathToCSV, destinationPath, 
                        downloadMediaCheckbox, unarchiveChatsCheckbox, statesDict, output, language):

        paths_parser = self.getParser()
        
        timestamp = self.getTimeStamp();
        # Entro nella cartella di destinazione (es. ../Output/)
        os.chdir(destinationPath)
        # Creo la cartella SCRAPED_timestamp
        os.mkdir(SCRAPING_DIRECTORY_NAME + "_" + timestamp)
        logging.info(f'Ho creato la cartella {SCRAPING_DIRECTORY_NAME}' + '_' + timestamp)
        # Ci entro (../Output/SCRAPED_timestamp/)
        os.chdir(SCRAPING_DIRECTORY_NAME + "_" + timestamp)
        
        self.get(BASE_URL)
        self.maximize_window()
        self.waitForElementToAppear(500, XPATH_CHAT_FILTER_BUTTON)
        output.config(text=statesDict['caricamento'])
        time.sleep(40)
        
        if(unarchiveChatsCheckbox == 1):
            unarchivedContacts = self.unarchiveChats()
        
        endOfSearch = False
        
        pixels = 0
        pre_height = 0
        new_height = 0
        nScrolls = 0
        
        scriptGoBack = "document.getElementById('" + CHAT_SECTION_HTML_ID + "').scrollTo(0," + "-document.getElementById('" + CHAT_SECTION_HTML_ID + "').scrollHeight)"
        
        if(len(pathToCSV) != 0):
            
            contactNamesFromCSV = self.readContactsFromFile(pathToCSV)
            
            for contactName in contactNamesFromCSV:

                logging.info('---------------------------------------------------------------------')
                time.sleep(10)
                logging.info(f'Sto esaminando il contatto {contactName}')                

                chats = self.getContacts()
                
                contactFound = self.searchContactToClick(chats, contactName)
                if(contactFound == True):
                    
                    logging.info(f'Contatto {contactName} trovato')
                    
                    path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                    # Al metodo getConversation() passo il percorso /SCRAPED_timestamp/
                    self.getConversation(path, contactName, tree, language)

                    
                    if(downloadMediaCheckbox == 1):
                        # Torno nella cartella ../Output/
                        os.chdir(destinationPath)
                        self.downloadMedia(statesDict, output)
                        logging.info('... FINE SCARICAMENTO MEDIA')
                        # Una volta scaricati i file, li metto nella cartella ../Output/SCRAPED_timestamp/nome_contatto/
                        self.moveFilesToMainDirectory(destinationPath + "\\" + path + "\\" + contactName, paths_parser)
                        logging.info('... Fine spostamento media')
                        # I file vengono zippati nella stessa cartella
                        self.zipFiles(destinationPath + "\\" + path + "\\" + contactName, contactName)
                        self.zipHasher(destinationPath + "\\" + path + "\\" + contactName)

                else:
                    
                    while True:
                        updatedList = []
                        nScrolls += 1
                        pixels += PIXELS_TO_SCROLL
                        self.execute_script('document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTo(0,' + str(pixels) + ')')
                        new_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
                        
                        while True:
                            try:
                                self.implicitly_wait(200)
                                scrolledChats = self.getContacts()
                                
                                updatedList = self.updateList(chats, scrolledChats)
                                
                                contactFoundInScrolledChats = self.searchContactToClick(updatedList, contactName)
                                
                                if(contactFoundInScrolledChats == True):
                                    endOfSearch = True
                                    path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                                    self.getConversation(path, contactName, tree)
                                    os.chdir(r'C:\GitHub_Repositories\WhatsApp_Scraper')
                                    self.execute_script(scriptGoBack)
                                
                                    if(downloadMediaCheckbox == 1):
                                        # Torno nella cartella ../Output/
                                        os.chdir(destinationPath)
                                        self.downloadMedia(statesDict, output)
                                        # Una volta scaricati i file, li metto nella cartella ../Output/SCRAPED_timestamp/nome_contatto/
                                        self.moveFilesToMainDirectory(destinationPath + "\\" + path + "\\" + contactName, paths_parser)
                                        # I file vengono zippati nella stessa cartella
                                        self.zipFiles(destinationPath + "\\" + path + "\\" + contactName, contactName)
                                        self.zipHasher(path + "\\" + contactName)
                                        self.execute_script(scriptGoBack)
                                    
                                    break
                                
                                logging.info('---------------------------------------------------------------------')
                                
                                break
                            except:
                                self.implicitly_wait(0.5)
                                
                        if(endOfSearch):
                            break
                        
                        if(pre_height < new_height):
                            pre_height = self.execute_script('return document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTop')
                        else:
                            break
        
        else:
            self.getAllChatsDefault(timestamp, downloadMediaCheckbox, tree, destinationPath, statesDict, output,
                                    paths_parser)
                    
        if(unarchiveChatsCheckbox == 1):
            self.archiveChats(unarchivedContacts)
     
    

    def archiveChats(self, unarchivedContacts):
        
        setUnarchivedChats = set(unarchivedContacts)
        pixels = 0
        archivedContacts = []
        scriptGoBack = "document.getElementById('" + CHAT_SECTION_HTML_ID + "').scrollTo(0," + "-document.getElementById('" + CHAT_SECTION_HTML_ID + "').scrollHeight)"
        
        while len(unarchivedContacts) != 0:
            chats2 = []
            self.execute_script('document.getElementById("' + CHAT_SECTION_HTML_ID + '").scrollTo(0,' + str(pixels) + ')')
            chats = self.getContacts()
            chatsAsStrings = self.fillNameList(chats)
            setChats = set(chatsAsStrings)
            setContactsToArchive = setUnarchivedChats.intersection(setChats)
            
            if(len(setContactsToArchive) == 0):
                pixels += PIXELS_TO_SCROLL
                continue
            else:
                
                for c in chats:
                    if(len(c.get_attribute('title')) != 0):
                        chats2.append(c)
                
                for chat in chats2:
                    name = chat.get_attribute('title')
                    if(name in list(setContactsToArchive) and name not in archivedContacts):
                        logging.info(f'Sto cercando di archiviare il contatto {name}')
                        time.sleep(2)
                        ActionChains(self).move_to_element(chat).perform()
                        time.sleep(1)
                        dropDownArchiveButton = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_ARCHIVED_CHATS)
                        dropDownArchiveButton.click()
                        time.sleep(1)
                        archiveButton = self.find_element(by=By.XPATH, value=XPATH_UNARCHIVE_BUTTON)
                        archiveButton.click()
                        time.sleep(5)
                        archivedContacts.append(name)
                        unarchivedContacts.pop()
                        self.execute_script(scriptGoBack)
                        break
                        
                pixels += PIXELS_TO_SCROLL
            
        
     
                    
    def readContactsFromFile(self, pathToFile):
        contacts = pd.read_csv(pathToFile)
        return contacts['Nome'].values
    
    
    
    def getConversation(self, pathToCSV, contactName, tree, language):
        
        try:
        
            logging.info(f'Sto cercando di recuperare la conversazione con {contactName}...')
            
            messageMetadataList = []
            # Retrieving all divs containing text messages
            messages = self.find_elements(by=By.XPATH, value=XPATH_TEXT_MESSAGES_CONTAINERS)
            
            # Retrieving text messages
            textMessages = self.find_elements(by=By.XPATH, value=XPATH_TEXT_MESSAGES)
            
            numMessages = len(textMessages)
            
            logging.info(f'Sono stati trovati {numMessages} messaggi di testo')
            
            if(len(messages) == 0 or len(textMessages) == 0):
                logging.error('QUESTA CHAT NON CONTIENE MESSAGGI DI TESTO')
                raise NoMessagesException("QUESTA CHAT NON CONTIENE MESSAGGI DI TESTO!")
            else:
            
                for message in messages:
                    
                    # Getting metadata for every message (sender, date and hour)
                    metadata = message.find_element(
                        by=By.XPATH,    
                        value=XPATH_SENDER
                    ).get_attribute("data-pre-plain-text")
                    
                    messageMetadataList.append(metadata)
        
                # Messages are sorted in descending order (if the last attribute is set to "True")
                sortedMetadataDict = self.sortMessagesByTime(messageMetadataList, textMessages, True, language)
                 
                for row in sortedMetadataDict:
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
                    
                    # A questo punto, siamo nella cartella /SCRAPED_timestamp/
                        # A .csv file named as the contact name the scraper is processing is created
                    self.makeCSV(dataToAppend[0], pathToCSV, contactName, tree)
                
        except NoMessagesException as nme:
            print(nme)
    
    
    
    def sortMessagesByTime(self, messageMetadataList, textMessages, reverse, language):
        
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
     
    
    
    def downloadMedia(self, statesDict, output):
        
        logging.info('STO SCARICANDO I MEDIA...')
        
        self.downloadImages(statesDict, output)
        self.downloadVideos(statesDict, output)
        self.downloadGIF(statesDict, output)
        self.downloadAudios(statesDict, output)
        self.downloadDocuments(statesDict, output)
    


    def downloadAudios(self, statesDict, output):
        
        logging.info('Sto cercando gli audio...')
        
        output.config(text=statesDict['aud'])
        
        time.sleep(10)
        
        try:
            audios = self.find_elements(by=By.XPATH, value=XPATH_AUDIOS)
            
            numAudios = len(audios)
            
            logging.info(f'Sono stati trovati {numAudios} audio')
        
            if(len(audios) != 0):

                for audio in audios:
                    
                    time.sleep(3)
                    
                    ActionChains(self).move_to_element(audio).perform()
                    
                    time.sleep(3)
                    
                    dropDownMenu = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_DOWNLOAD_AUDIOS)
                    
                    dropDownMenu.click()
                    
                    time.sleep(3)
                    
                    downloadButton = self.find_element(by=By.XPATH, value=XPATH_DOWNLOAD_AUDIOS)
                    
                    downloadButton.click()
                    
            else:
                logging.error('AUDIO NON PRESENTI')
                raise AudioNotFoundException("AUDIO NON PRESENTI! \n")
                
        except AudioNotFoundException as anf:
            print(anf)
        


    def downloadImages(self, statesDict, output):

        logging.info('Sto cercando le immagini...')
        
        output.config(text=statesDict['img'])

        time.sleep(10)
        
        try:
            images = self.find_elements(by=By.XPATH, value=XPATH_IMAGES)
            
            numImages = len(images)
            
            logging.info(f'Sono state trovate {numImages} immagini')
            
            if(len(images) != 0):

                for image in images:
                    
                    time.sleep(3)
                    
                    image.click()
    
                    time.sleep(3)
                    
                    downloadButton = self.find_element(by=By.XPATH, value=DOWNLOAD_BUTTON_XPATH)
                    
                    downloadButton.click()
                    
                    logging.debug('Ho cliccato sul tasto download')
                    
                    time.sleep(3)
                    
                    closeButton = self.find_element(by=By.XPATH, value=CLOSE_BUTTON_MEDIA_XPATH)
                    
                    closeButton.click()
            else:
                logging.error('IMMAGINI NON PRESENTI')
                raise ImageNotFoundException("IMMAGINI NON PRESENTI! \n")
            
        except ImageNotFoundException as inf:
            print(inf)
        
    
    
    def downloadVideos(self, statesDict, output):
        
        logging.info('Sto cercando i video...')
        
        output.config(text=statesDict['vid'])
        
        time.sleep(10)
        
        try:
            
            videoPlayers = self.find_elements(by=By.XPATH, value=VIDEO_PLAY_BUTTON_XPATH)
            
            numVideos = len(videoPlayers)
            
            logging.info(f'Sono stati trovati {numVideos} video')
            
            if(len(videoPlayers) != 0):

                for playButton in videoPlayers:
                    
                    time.sleep(3)
                    
                    playButton.click()
                    
                    time.sleep(60)
                    
                    downloadButton = self.find_element(by=By.XPATH, value=DOWNLOAD_BUTTON_XPATH)
                    
                    downloadButton.click()
                    
                    time.sleep(3)
                    
                    closeButton = self.find_element(by=By.XPATH, value=CLOSE_BUTTON_MEDIA_XPATH)
                    
                    closeButton.click()
                    
            else:
                logging.error('VIDEO NON PRESENTI')
                raise VideoNotFoundException("VIDEO NON PRESENTI! \n")
                    
        except VideoNotFoundException as vnf:
            print(vnf)
            
           
            
    def downloadDocuments(self, statesDict, output):

        logging.info('Sto cercando i documenti...')

        output.config(text=statesDict['doc'])

        time.sleep(10)
        
        try:
            
            docList = self.find_elements(by=By.XPATH, value=XPATH_DOC_LIST)
            
            numDocs = len(docList)
            
            logging.info(f'Sono stati trovati {numDocs} documenti')
            
            if(len(docList) != 0):

                for doc in docList:
                    
                    time.sleep(3)
                    
                    doc.click()
                    
                    time.sleep(3)
                    
            else:
                logging.error('DOCUMENTI NON PRESENTI')
                raise DocumentNotFoundException("DOCUMENTI NON PRESENTI! \n")
        
        except DocumentNotFoundException as dnf:
            print(dnf)
            
            
            
    def downloadGIF(self, statesDict, output):

        logging.info('Sto cercando le GIF...')

        output.config(text=statesDict['doc'])

        time.sleep(10)
        
        try:
            
            GIFList = self.find_elements(by=By.XPATH, value=XPATH_GIFS)
            
            numGifs = len(GIFList)
            
            logging.info(f'Sono state trovate {numGifs} GIF')
            
            if(len(GIFList) != 0):

                for gif in GIFList:
                    
                    time.sleep(3)
                    
                    ActionChains(self).move_to_element(gif).perform()
                    
                    time.sleep(3)
                    
                    dropDownMenu = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_DOWNLOAD_AUDIOS)
                    
                    time.sleep(3)
                    
                    dropDownMenu.click()
                    
                    time.sleep(3)
                    
                    downloadButton = self.find_element(by=By.XPATH, value=XPATH_DOWNLOAD_AUDIOS)
                    
                    downloadButton.click()
                    
                    time.sleep(3)
                    
            else:
                logging.error('GIF NON PRESENTI')
                raise DocumentNotFoundException("GIF NON PRESENTI! \n")
        
        except DocumentNotFoundException as dnf:
            print(dnf)
    
    
    
    def makeCSV(self, data, pathToCSV, contactName, tree):
        
        tupla = (data[0], data[1], data[2], data[3])
        tree.insert('', tk.END, values=tupla)
        
        if(not self.isFileNameValid(contactName)):
            
            contactName = self.renameFileOrFolderName(contactName)
            
            if not os.path.exists(contactName):
                
                os.mkdir(contactName)
                
            os.chdir(contactName)
            
        else:
            
            if not os.path.exists(contactName):
                
                os.mkdir(contactName)
                
            os.chdir(contactName)
        
        if not os.path.exists(contactName + ".csv"):
            newDataFrame = pd.DataFrame([data], columns=HEADER)
            newDataFrame.to_csv(contactName + ".csv", mode='a', index=False, header=True, sep=";")
        else:
            newDataFrame = pd.DataFrame([data], columns=HEADER)
            newDataFrame.to_csv(contactName + ".csv", mode='a', index=False, header=False, sep=";")
        
        # Una volta aggiornato il file .csv, torno indietro di un livello
        os.chdir('..')
        
        
     
    def isFileNameValid(self, fileName):
        return not any([char in fileName for char in CHARACTERS_TO_AVOID])    
    
   
    
    def renameFileOrFolderName(self, fileName):
        return "".join(re.split(REGULAR_EXPRESSION, fileName))
    
    
        
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

            
            
    def moveFilesToMainDirectory(self, destinationPath, paths_parser):
        
        os.chdir(paths_parser[PATHS][DOWNLOADS_PATH])
        
        downloads_path = paths_parser[PATHS][DOWNLOADS_PATH]
        directory_callback = paths_parser[PATHS][DIRECTORY_CALLBACK]
        
        logging.info(f'Sono entrato nella cartella {downloads_path} e sto spostando i file in {destinationPath}')
        
        filesInDownloadsFolder = os.listdir()
        filteredFiles = [i for i in filesInDownloadsFolder if any(i for j in ACCEPTED_EXTENSIONS if str(j) in i)]
        
        for fileName in filteredFiles:
            newFileName = self.fixFileName(fileName)
            if(pathlib.Path(newFileName).suffix in ACCEPTED_EXTENSIONS):
                os.rename(fileName, newFileName)
                shutil.move(newFileName, destinationPath)
            
        os.chdir(paths_parser[PATHS][DIRECTORY_CALLBACK])
        logging.info(f'Sono tornato nella cartella {directory_callback}')
        
    
    
    def fixFileName(self, fileName):
        newFileName = fileName.split(pathlib.Path(fileName).suffix)
        newFileName = newFileName[0]
        newFileName = newFileName.replace(".","_")
        newFileName += (pathlib.Path(fileName).suffix)
        return newFileName
    
    
    
    def zipFiles(self, path, contactName):
        os.chdir(path)
        logging.info(f'Sono entrato nella cartella del contatto {contactName} per zippare i file...')
        # Zipping multimedia files
        with zipfile.ZipFile(contactName + "_" + MULTIMEDIA_ZIP_NAME + ".zip", "w", compression=zipfile.ZIP_DEFLATED) as f:
            for file in os.listdir():
                if(file != contactName + ".csv" and not file.endswith(".zip")):
                    f.write(file)
        # Zipping .csv file
        with zipfile.ZipFile(contactName + ".zip", "w", compression=zipfile.ZIP_DEFLATED) as f:
            for file in os.listdir():
                if(file == contactName + ".csv" and not file.endswith(".zip")):
                    f.write(file)
                    
        os.chdir('..')  
        
                    
                    
    def zipHasher(self, path):
        
        # Entro nella cartella del contatto
        os.chdir(path)
        
        for fileName in os.listdir():
            
            data = []
            sha512 = hashlib.sha512()
            md5 = hashlib.md5()
            
            if(fileName.endswith(".zip")):
                with open(fileName, "rb") as f:
                    # Read and update hash string value in blocks of 4K
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha512.update(chunk)
                        md5.update(chunk)
                        
                    logging.info(f'Message digest del file {fileName} generato con algoritmo ' + '{}'.format(sha512.name) + ' {}'.format(sha512.hexdigest()))
                    logging.info(f'Message digest del file {fileName} generato con algoritmo ' + '{}'.format(md5.name) + ' {}'.format(md5.hexdigest()))
                    
                    data.append(fileName)
                    data.append(md5.hexdigest())
                    data.append(sha512.hexdigest())
                    
                    if not os.path.exists(HASHING_CSV_FILE_NAME):
                        newDataFrame = pd.DataFrame([data], columns=HEADER_HASHING)
                        newDataFrame.to_csv(HASHING_CSV_FILE_NAME, mode='a', index=False, header=True, sep=";")
                    else:
                        newDataFrame = pd.DataFrame([data], columns=HEADER_HASHING)
                        newDataFrame.to_csv(HASHING_CSV_FILE_NAME, mode='a', index=False, header=False, sep=";")
        
        os.chdir('..')