import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import constants


#set more data to true to get more results
class usaNewsSchoolsStats(object):
    
    def __init__(self, moreData, csvFileName):
        self.outputNameCSV = csvFileName
        self.moreData = moreData
        self.fileName = fileName
        self.url = ''
        self.headers = {"User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
        self.url = constants.USA_NEWS_SCHOOL_URL



    def getUsaNewsSchoolsHTML(self):
        url = self.url
        r = requests.get(url,headers=self.headers)
        soup = BeautifulSoup(r.text, features="lxml")
        return soup
    
    def getContentsWhenPageScrolls(self):
        url = self.getSchoolsUrl()

        browser = webdriver.Chrome('chromedriver.exe')

        browser.get(url)
        time.sleep(1)

        elem = browser.find_element_by_tag_name("body")
        no_of_pagedowns = 10
        while no_of_pagedowns:
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)
            no_of_pagedowns-=1
        html = browser.page_source

        soup = BeautifulSoup(html)

        return soup

    def getTopSchoolLinks(self, html):
        linkList = []
        for link in html.select('h3 a'):
            href = link.get('href')
            linkList.append(href)
        return linkList
    
    def getSchoolStats(self, links):
        schoolLstWithStats = []
        linkList = links
        for link in linkList:
            schoolStats = {}
            schoolSoup = self.makeSchoolRequest(link)
            schoolSoupStrong = schoolSoup.select('strong')

            schoolName = schoolSoup.find('h1').text
            schoolStats['institution'] = schoolName

            for i, j in zip(schoolSoup.select('dl dt'), schoolSoup.select('dl dd')):
                schoolStats[i.text] = j.text
            
            schoolRank = schoolSoupStrong[:2]
            rankTitle = schoolRank[1].text
            rankScore = schoolRank[0].text

            schoolStats[rankTitle] = rankScore

            tracks = self.getSchoolTracks(schoolSoupStrong)
            schoolStats["concentrations"] = tracks
            schoolLstWithStats.append(schoolStats)
        return schoolLstWithStats

    def makeSchoolRequest(self, link):
        r = requests.get(link,headers=self.headers)
        soup = BeautifulSoup(r.text, features="lxml")
        return soup
    
    
    def getSchoolTracks(self, trackHTML):
        schoolTracks = trackHTML[2:]
        tracks = []
        for i in schoolTracks:
            text = i.text
            if constants.SCHOOL_TRACK not in text and len(text) > 3 and "Previous:" not in text and "Next:" not in text:
                if text not in tracks:
                    tracks.append(text)
        return tracks

    def dataFrameGen(self, csvGen):
        self.fileName += ".csv"
        if self.moreData:
            mbaHtml = self.getContentsWhenPageScrolls()
        else:
            mbaHtml = self.getUsaNewsSchoolsHTML()
        schoolLinks = self.getTopSchoolLinks(mbaHtml)
        schoolStatLst = self.getSchoolStats(schoolLinks)

        schoolDf = pd.DataFrame(schoolStatLst)
        schoolDf.set_index('institution')
        if csvGen:
            schoolDf.to_csv(self.fileName)

        return schoolDf

#set more data to true to get more results
a = usaNewsSchoolsStats( False, 'nameOfYourCsvFile')
#set to false to not generate csv file
b = a.dataFrameGen(True)
b.groupby('institution')