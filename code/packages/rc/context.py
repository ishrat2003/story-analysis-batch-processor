from lc.story import Story
from file.json import Json as JsonFile
from utility.date_processor import DateProcessor
from story.rc import RCStory
import sys
import regex as re

class Context:
    
    def __init__(self, loader, writer):
        self.loader = loader
        self.writer = writer
        self.story = RCStory(self.writer.getPath())
        self.dateProcessor = DateProcessor()
        self.total = 0
        self.documents = []
        self.documentsData = {}
        self.datedCount = {}
        return
    
    def getData(self):
        return {
            'total': self.total,
            'dated_count': self.datedCount,
            'documents': self.documentsData
        }
    
    def process(self, filePath, wordKey, startDate, endDate):
        file = JsonFile()
        data = file.read(filePath)
        if not data:
            return
        
        self.termboardTopics = wordKey.split(",")
        
        if startDate:
            self.startDate = self.dateProcessor.strToDate(startDate)
            
        if endDate:
            self.endDate = self.dateProcessor.strToDate(endDate)
        
        self.loadDocuments(data)
        
        data = self.getData()
        if data:
            fileName = self.getRcFileName()
            self.writer.save(fileName, data)  
        return True
    
    
    def loadDocuments(self, data):
        if not data or 'documents' not in data.keys():
            return

        self.matchRequired = len(self.termboardTopics)
        
        self.total = 0
        years = data['documents'].keys()
        if not len(years):
            return
        for year in years:
            months = data['documents'][year].keys()
            if not len(months):
                continue
            for month in months:
                days = data['documents'][year][month].keys()
                if not len(days):
                    continue
                for day in days:
                    fullDateKey = year + '-' + self.dateProcessor.getFormattedMonthOrDay(month) + '-' + self.dateProcessor.getFormattedMonthOrDay(day)
                    fullDateObject = self.dateProcessor.strToDate(fullDateKey)
                    totalMatch = 0
                    
                    for link in data['documents'][year][month][day].keys():
                        if (link in self.documents) or (fullDateObject < self.startDate) or (fullDateObject > self.endDate):
                            continue
                        
                        topicKeys = data['documents'][year][month][day][link]['topics'].keys()
                        matchedItems = list(set(topicKeys) & set(self.termboardTopics))
                        
                        if self.matchRequired == len(matchedItems):
                            self.processDocument(link, fullDateKey)
                            self.documents.append(link)
                            totalMatch += 1
                            self.total += 1
                    
                    if totalMatch > 0:
                        self.datedCount[fullDateKey]= totalMatch
                        
        return
    
    def processDocument(self, link, fullDateKey):
        print(link)
        documentData = self.loader.fetchPage(link)
        if not documentData or 'content' not in documentData.keys():
            return
        
        text = self.loader.getContent(documentData)
        if fullDateKey not in self.documentsData.keys():
            self.documentsData[fullDateKey] = {}
            
        year, month, day = fullDateKey.split('-')
        if year not in self.documentsData.keys():
            self.documentsData[year] = {}
        if month not in self.documentsData[year].keys():
            self.documentsData[year][month] = {}
        if day not in self.documentsData[year][month].keys():
            self.documentsData[year][month][day] = {}
            
        self.documentsData[year][month][day][link] = {
            'link': documentData['link'],
            'title': documentData['title'],
            'pubDate': fullDateKey,
            'description': documentData['description'],
            'story_words': self.story.getContextualWords(text)
        }
        
        return
    
    def getRcFileName(self):
        context = self.termboardTopics
        if self.startDate:
            context.append(self.dateProcessor.dateToString(self.startDate))
        context.append('__')
        if self.endDate:
            context.append(self.dateProcessor.dateToString(self.endDate))
        return '_'.join([str(x) for x in context])
    

    
    