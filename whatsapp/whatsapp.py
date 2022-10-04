# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 12:10:34 2022
@author: guido
"""

import time

from datetime import datetime

import os

import re

import pathlib

import shutil

import zipfile

import hashlib

from selenium import webdriver

import tkinter as tk

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
from whatsapp.constants import DOWNLOADS_PATH
from whatsapp.constants import XPATH_PDF_LIST
from whatsapp.constants import ACCEPTED_EXTENSIONS
from whatsapp.constants import XPATH_CHAT_FILTER_BUTTON
from whatsapp.constants import MULTIMEDIA_ZIP_NAME
from whatsapp.constants import HASHING_CSV_FILE_NAME
from whatsapp.constants import CLOSE_ARCHIVED_CHATS_SECTION
from whatsapp.constants import CHARACTERS_TO_AVOID
from whatsapp.constants import REGULAR_EXPRESSION

import pandas as pd

from whatsapp.exceptions.ImageNotFoundException import ImageNotFoundException
from whatsapp.exceptions.VideoNotFoundException import VideoNotFoundException
from whatsapp.exceptions.AudioNotFoundException import AudioNotFoundException
from whatsapp.exceptions.DocumentNotFoundException import DocumentNotFoundException
from whatsapp.exceptions.ArchivedChatsButtonNotFoundException import ArchivedChatsButtonNotFoundException

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
                raise ArchivedChatsButtonNotFoundException("ERRORE! IL BOTTONE DELLE CHAT ARCHIVIATE NON E' PRESENTE! \n")
            else:
                self.wait(5)
                self.waitForElementToAppear(500, ARCHIVED_CHATS_BUTTON)
                
                archivedChatsButton[0].click()
                
                self.wait(5)
        
                unarchivedContacts = []
                archivedChats2 = []
                    
                archivedChats = self.find_elements(by=By.XPATH, value=XPATH_ARCHIVED_CHATS)
                
                for a in archivedChats:
                    if(len(a.get_attribute('title')) != 0):
                        archivedChats2.append(a)
        
                for chat in archivedChats2:
                    if(chat.is_displayed()):
                        unarchivedContacts.append(chat.get_attribute('title'))
                        self.wait(2)
                        ActionChains(self).move_to_element(chat).perform()
                        self.wait(1)
                        dropDownArchivedChatButton = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_ARCHIVED_CHATS)
                        dropDownArchivedChatButton.click()
                        self.wait(1)
                        unarchiveButton = self.find_element(by=By.XPATH, value=XPATH_UNARCHIVE_BUTTON)
                        unarchiveButton.click()
                        self.wait(5)
                
                closeArchivedChatsSectionButton = self.find_element(by=By.XPATH, value=CLOSE_ARCHIVED_CHATS_SECTION)
                closeArchivedChatsSectionButton.click()
                
                return unarchivedContacts
            
        except ArchivedChatsButtonNotFoundException as acb:
            print(acb)
          


    def getAllChatsDefault(self, timestamp, downloadMediaCheckbox):
        
        pixels = 0
        pre_height = 0
        new_height = 0
        nScrolls = 0
        
        endOfSearch = False
        
        chats = self.getContacts()
        newChats = []
        
        print('Prima dello scroll erano presenti: \n')
        for c in chats:
            if(len(c.get_attribute('title')) != 0):
                print(c.get_attribute('title'))
                print('\n')
                
        
        for chat in chats:
            contactName = chat.get_attribute('title')
            if(len(contactName) != 0):
                
                path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                contactFound = self.searchContactToClick(chats, contactName)
                if(contactFound == True):
                    self.getConversation(path, contactName)
                
                    if(downloadMediaCheckbox == True):
                        os.chdir(DIRECTORY_CALLBACK)
                        self.downloadMedia()
                        print('Devo spostare i file: sono in ' + os.getcwd() + "\n")
                        self.moveFilesToMainDirectory(DIRECTORY_CALLBACK + "\\" + path + "\\" + contactName)
                        self.zipFiles(DIRECTORY_CALLBACK + "\\" + path + "\\" + contactName, contactName)
                        self.zipHasher(DIRECTORY_CALLBACK + "\\" + path + "\\" + contactName)
                
        
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
                    scrolledChats = self.getContacts()
                    updatedList = self.updateList(chats, scrolledChats)
                    print('Dopo lo scroll ci sono: \n')
                    for c in updatedList:
                        if(len(c.get_attribute('title')) != 0):
                            print(c.get_attribute('title'))
                            print('\n')
                        if("/" in c.get_attribute('title')):
                            (c.get_attribute('title')).replace("/", "_")
                    
                    for scrolledChat in updatedList:
                        contactName = scrolledChat.get_attribute('title')
                        if(len(contactName) != 0):
                            path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                            contactFound = self.searchContactToClick(scrolledChats, contactName)
                            if(contactFound == True):
                                self.getConversation(path, contactName)
                    
                                if(downloadMediaCheckbox == True):
                                    os.chdir(DIRECTORY_CALLBACK)
                                    self.downloadMedia()
                                    print('Devo spostare i file: sono in ' + os.getcwd() + "\n")
                                    self.moveFilesToMainDirectory(DIRECTORY_CALLBACK + "\\" + path + "\\" + contactName)
                                    self.zipFiles(DIRECTORY_CALLBACK + "\\" + path + "\\" + contactName, contactName)
                                    self.zipHasher(DIRECTORY_CALLBACK + "\\" + path + "\\" + contactName)
                    
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
    

    
    def findChatToScrap(self, tree, pathToCSV, destinationPath):
        
        print('Estraggo le chat dal file ' + pathToCSV)
        
        unarchiveChatsCheckbox = False
        downloadMediaCheckbox = True
        
        timestamp = self.getTimeStamp();
        os.chdir(destinationPath)
        print('RIGA 267: Sono nella cartella ' + os.getcwd() + '\n')
        os.mkdir(SCRAPING_DIRECTORY_NAME + "_" + timestamp)
        os.chdir(SCRAPING_DIRECTORY_NAME + "_" + timestamp)
        print('RIGA 271: Sono entrato nella cartella appena creata, ovvero ' + os.getcwd() + '\n')
        
        self.get(BASE_URL)
        self.maximize_window()
        self.waitForElementToAppear(500, XPATH_CHAT_FILTER_BUTTON)
        self.wait(40)
        if(unarchiveChatsCheckbox == True):
            print('Unarchiving chats... \n')
            unarchivedContacts = self.unarchiveChats()
        
        endOfSearch = False
        
        pixels = 0
        pre_height = 0
        new_height = 0
        nScrolls = 0
        
        scriptGoBack = "document.getElementById('" + CHAT_SECTION_HTML_ID + "').scrollTo(0," + "-document.getElementById('" + CHAT_SECTION_HTML_ID + "').scrollHeight)"
        
        contactNamesFromCSV = self.readContactsFromFile(pathToCSV)
        
        if(len(contactNamesFromCSV) == 0):
            self.getAllChatsDefault(timestamp, downloadMediaCheckbox)
        else:
            for contactName in contactNamesFromCSV:
        
                print('Cercando ' + contactName + '... \n')
                
                chats = self.getContacts()
                
                print('Prima di scrollare erano presenti: \n')
                chatsAsStrings = self.fillNameList(chats)
                print(chatsAsStrings)
                
                contactFound = self.searchContactToClick(chats, contactName)
                if(contactFound == True):
                    print('Contatto trovato senza scrollare \n')
                    path = SCRAPING_DIRECTORY_NAME + "_" + timestamp
                    print('RIGA 309: Sono ancora nella cartella ' + os.getcwd() + ' e chiamo il metodo getConversation() \n')
                    self.getConversation(path, contactName, tree)
                    print('FINE \n')
                    os.chdir(r'C:\GitHub_Repositories\WhatsApp_Scraper')
                    
                    if(downloadMediaCheckbox == True):
                        os.chdir(destinationPath)
                        self.downloadMedia()
                        print('Devo spostare i file: sono in ' + os.getcwd() + "\n")
                        self.moveFilesToMainDirectory(destinationPath + "\\" + path + "\\" + contactName)
                        self.zipFiles(destinationPath + "\\" + path + "\\" + contactName, contactName)
                        self.zipHasher(path + "\\" + contactName)
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
                                    self.getConversation(path, contactName, tree)
                                    self.execute_script(scriptGoBack)
                                
                                    if(downloadMediaCheckbox == True):
                                        os.chdir(path)
                                        self.downloadMedia()
                                        print('Devo spostare i file: sono in ' + os.getcwd() + "\n")
                                        self.moveFilesToMainDirectory(path + "\\" + contactName)
                                        self.zipFiles(path + "\\" + contactName, contactName)
                                        self.execute_script(scriptGoBack)
                                        self.zipHasher(path + "\\" + contactName)
                                    
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
            
                    
        if(unarchiveChatsCheckbox == True):
            print('Re-archiving chats... \n')
            self.archiveChats(unarchivedContacts)
     
    

    def archiveChats(self, unarchivedContacts):
        
        setUnarchivedChats = set(unarchivedContacts)
        pixels = 0
        # Lista di stringhe
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
                
                print('Stampo il contenuto di chats: \n')
                for c in chats:
                    if(len(c.get_attribute('title')) != 0):
                        chats2.append(c)
                print(self.fillNameList(chats2))
                
                print('\n ### \n')
                print('Stampo le chat da archiviare: \n')
                print(unarchivedContacts)
                
                
                for chat in chats2:
                    name = chat.get_attribute('title')
                    print('Sto cercando di prendere il contatto ' + name)
                    print('\n')
                    if(name in list(setContactsToArchive) and name not in archivedContacts):
                        self.wait(2)
                        ActionChains(self).move_to_element(chat).perform()
                        self.wait(1)
                        dropDownArchiveButton = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_ARCHIVED_CHATS)
                        dropDownArchiveButton.click()
                        self.wait(1)
                        archiveButton = self.find_element(by=By.XPATH, value=XPATH_UNARCHIVE_BUTTON)
                        archiveButton.click()
                        self.wait(5)
                        archivedContacts.append(name)
                        unarchivedContacts.pop()
                        self.execute_script(scriptGoBack)
                        break
                        
                pixels += PIXELS_TO_SCROLL
            
        
     
                    
    def readContactsFromFile(self, pathToFile):
        contacts = pd.read_csv(pathToFile)
        return contacts['Nome'].values
    
    
    
    def getConversation(self, pathToCSV, contactName, tree):
        
        print('Getting conversation with ' + contactName + '... \n')
        
        messageMetadataList = []
        # Retrieving all divs containing text messages
        messages = self.find_elements(by=By.XPATH, value=XPATH_TEXT_MESSAGES_CONTAINERS)
        
        # Retrieving text messages
        textMessages = self.find_elements(by=By.XPATH, value=XPATH_TEXT_MESSAGES)
        
        for message in messages:
            
            # Getting metadata for every message (sender, date and hour)
            metadata = message.find_element(
                by=By.XPATH,    
                value=XPATH_SENDER
            ).get_attribute("data-pre-plain-text")
            
            messageMetadataList.append(metadata)

        # Messages are sorted in descending order (if the last attribute is set to "True")
        sortedMetadataDict = self.sortMessagesByTime(messageMetadataList, textMessages, True)
         
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
            
            print('RIGA 482: Chiamo il metodo makeCSV() a cui passo il percorso ' + pathToCSV + '\n')
                # A .csv file named as the contact name the scraper is processing is created
            self.makeCSV(dataToAppend[0], pathToCSV, contactName, tree)
    
        
    
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
     
    
    
    def downloadMedia(self):
        
        self.downloadAudios()
        self.downloadImages()
        self.downloadVideos()
        self.downloadDocuments()
    


    def downloadAudios(self):
        
        print('Downloading audios... \n')
        
        # self.wait(10)
        
        try:
            audios = self.find_elements(by=By.XPATH, value=XPATH_AUDIOS)
        
            if(len(audios) != 0):
                print(str(len(audios)) + ' audio(s) found... \n')
                for audio in audios:
                    
                    ActionChains(self).move_to_element(audio).perform()
                    
                    self.wait(3)
                    
                    dropDownMenu = self.find_element(by=By.XPATH, value=XPATH_DROP_DOWN_MENU_DOWNLOAD_AUDIOS)
                    
                    dropDownMenu.click()
                    
                    self.wait(3)
                    
                    downloadButton = self.find_element(by=By.XPATH, value=XPATH_DOWNLOAD_AUDIOS)
                    
                    downloadButton.click()
                    
            else:
                raise AudioNotFoundException("ERRORE! AUDIO NON PRESENTI! \n")
                
        except AudioNotFoundException as anf:
            print(anf)
        


    def downloadImages(self):
        print('Download images method called \n')
        try:
            images = self.find_elements(by=By.XPATH, value=XPATH_IMAGES)
            
            if(len(images) != 0):
                print(str(len(images)) + ' image(s) found... \n')
                for image in images:
                    
                    self.wait(3)
                    
                    image.click()
    
                    self.wait(3)
                    
                    downloadButton = self.find_element(by=By.XPATH, value=DOWNLOAD_BUTTON_XPATH)
                    
                    downloadButton.click()
                    
                    self.wait(3)
                    
                    closeButton = self.find_element(by=By.XPATH, value=CLOSE_BUTTON_MEDIA_XPATH)
                    
                    closeButton.click()
            else:
                raise ImageNotFoundException("ERRORE! IMMAGINI NON PRESENTI! \n")
            
        except ImageNotFoundException as inf:
            print(inf)
        
    
    
    def downloadVideos(self):
        
        try:
            
            videoPlayers = self.find_elements(by=By.XPATH, value=VIDEO_PLAY_BUTTON_XPATH)
            
            if(len(videoPlayers) != 0):
                print(str(len(videoPlayers)) + ' video(s) found... \n')
                for playButton in videoPlayers:
                    
                    self.wait(3)
                    
                    playButton.click()
                    
                    self.wait(60)
                    
                    downloadButton = self.find_element(by=By.XPATH, value=DOWNLOAD_BUTTON_XPATH)
                    
                    downloadButton.click()
                    
                    self.wait(3)
                    
                    closeButton = self.find_element(by=By.XPATH, value=CLOSE_BUTTON_MEDIA_XPATH)
                    
                    closeButton.click()
            else:
                raise VideoNotFoundException("ERRORE! VIDEO NON PRESENTI! \n")
                    
        except VideoNotFoundException as vnf:
            print(vnf)
            
           
            
    def downloadDocuments(self):
        
        try:
            
            pdfList = self.find_elements(by=By.XPATH, value=XPATH_PDF_LIST)
            
            if(len(pdfList) != 0):
                print(str(len(pdfList)) + ' PDF(s) found... \n')
                for pdf in pdfList:
                    
                    self.wait(3)
                    
                    pdf.click()
                    
            else:
                raise DocumentNotFoundException("ERRORE! DOCUMENTI NON PRESENTI! \n")
        
        except DocumentNotFoundException as dnf:
            print(dnf)
    
    
    
    def makeCSV(self, data, pathToCSV, contactName, tree):
        
        tupla = (data[0], data[1], data[2], data[3])
        tree.insert('', tk.END, values=tupla)
        
        # os.chdir(pathToCSV)
        print('RIGA 654: Sono nella cartella ' + os.getcwd() + '\n')
        
        if(not self.isFileNameValid(contactName)):
            contactName = self.renameFileOrFolderName(contactName)
            if not os.path.exists(contactName):
                os.mkdir(contactName)
            os.chdir(contactName)
            print('Sono entrato nella cartella del contatto ' + contactName + '\n')
        else:
            if not os.path.exists(contactName):
                print('RIGA 664: La cartella ' + contactName + ' non esiste e la creo \n')
                os.mkdir(contactName)
                print('RIGA 666: Cartella ' + contactName + ' creata \n')
            os.chdir(contactName)
            print('RIGA 668: Sono nella cartella ' + os.getcwd() + '\n')
        
        print('Writing new data to csv... \n')
        print(data)
        
        if not os.path.exists(contactName + ".csv"):
            newDataFrame = pd.DataFrame([data], columns=HEADER)
            newDataFrame.to_csv(contactName + ".csv", mode='a', index=False, header=True, sep=";")
        else:
            newDataFrame = pd.DataFrame([data], columns=HEADER)
            newDataFrame.to_csv(contactName + ".csv", mode='a', index=False, header=False, sep=";")
            
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
    
    
    
    def wait(self, seconds):
        for i in range(1, seconds+1):
            time.sleep(1)
            print(str(i) + '... \n')
            
            
            
    def moveFilesToMainDirectory(self, destinationPath):
        
        print('Sposto i file in ' + destinationPath)
        
        os.chdir(DOWNLOADS_PATH)
        
        filesInDownloadsFolder = os.listdir()
        filteredFiles = [i for i in filesInDownloadsFolder if any(i for j in ACCEPTED_EXTENSIONS if str(j) in i)]
        
        print('File filtrati: \n')
        print(filteredFiles)
        
        for fileName in filteredFiles:
            newFileName = self.fixFileName(fileName)
            print('\n ######## newFileName = ' + newFileName + " ######## \n")
            if(pathlib.Path(newFileName).suffix in ACCEPTED_EXTENSIONS):
                os.rename(fileName, newFileName)
                shutil.move(newFileName, destinationPath)
                print('\n Il file ' + fileName + " è ancora nella cartella Downloads: \n")
                print(fileName in os.listdir())
            
        os.chdir(DIRECTORY_CALLBACK)
        
    
    
    def fixFileName(self, fileName):
        newFileName = fileName.split(pathlib.Path(fileName).suffix)
        newFileName = newFileName[0]
        newFileName = newFileName.replace(".","_")
        newFileName += (pathlib.Path(fileName).suffix)
        return newFileName
    
    
    
    def zipFiles(self, path, contactName):
        os.chdir(path)
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
                    
                    
                    
    def zipHasher(self, path):
        # os.chdir(path)
        
        print('Creating file ' + HASHING_CSV_FILE_NAME + '... \n')
        
        for fileName in os.listdir():
            
            data = []
            sha512 = hashlib.sha512()
            md5 = hashlib.md5()
            
            if(fileName.endswith(".zip")):
                print('Sono sul file ' + fileName + '... \n')
                with open(fileName, "rb") as f:
                    # Read and update hash string value in blocks of 4K
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha512.update(chunk)
                        md5.update(chunk)
                    print('{}: {}'.format(sha512.name, sha512.hexdigest()))
                    print('{}: {}'.format(md5.name, md5.hexdigest()))
                    data.append(fileName)
                    data.append(md5.hexdigest())
                    data.append(sha512.hexdigest())
                    if not os.path.exists(HASHING_CSV_FILE_NAME):
                        newDataFrame = pd.DataFrame([data], columns=HEADER_HASHING)
                        newDataFrame.to_csv(HASHING_CSV_FILE_NAME, mode='a', index=False, header=True, sep=";")
                    else:
                        newDataFrame = pd.DataFrame([data], columns=HEADER_HASHING)
                        newDataFrame.to_csv(HASHING_CSV_FILE_NAME, mode='a', index=False, header=False, sep=";")