import operator, math, datetime
from nltk import word_tokenize, pos_tag
from nltk.stem.porter import PorterStemmer
from utility.utility import Utility
import regex as re
import os, sys

class Hierarchy:
    
    def __init__(self):
        self.tree = {}
        self.documents = []
        self.pureWords = {}
        self.blockCounts = {}
        self.wordDocuments = {}
        self.allowedMinimum = 10
        self.filteredWords = []
        self.total = {}
        self.grandTotal = 0;
        return
    
    def getTree(self, data):
        if not data or 'documents' not in data.keys():
            return self.tree
        
        self.loadDocuments(data['documents'])
        self.loadFilteredWords()
        self.loadTree()

        return {
            'grand_total': self.grandTotal,
            'total': self.total,
            'tree': self.tree
        }
        
    def loadTree(self):
        parents = self.getParents(self.filteredWords)
        print(parents)
        return
    
    def getParents(self, setOfWords):
        commons = {}
        processedKeys = []
        for word1 in setOfWords:
            word1Documents = set(self.wordDocuments[word1])
            for word2 in setOfWords:
                if ((word1 == word2) or ((word1 + word2) in processedKeys)):
                    continue
                word2Documents = set(self.wordDocuments[word2])
                processedKeys.append(word1 + word2)
                processedKeys.append(word2 + word1)
                commonDocuments = word1Documents.intersection(word2Documents)
                if len(commonDocuments) < self.allowedMinimum:
                    continue
                commons[word1 + word2] = len(commonDocuments)
                
                print((word1 + word2), len(commonDocuments))
                
        print(len(commons))
        return
    
    def loadFilteredWords(self):
        allowedMin = self.grandTotal / 10
        words = self.blockCounts.keys()
        for word in words:
            if self.blockCounts[word] > allowedMin:
                # print(word, '-', self.blockCounts[word])
                self.filteredWords.append(word)
            else:
                del self.pureWords[word]
                del self.wordDocuments[word]
        return
    
    def loadDocuments(self, documents):
        for year in documents.keys():
            for month in documents[year].keys():
                for day in documents[year][month].keys():
                    for link in documents[year][month][day].keys():
                        fullDate = str(year) + '-' + str(month) + '-' + str(day)
                        if fullDate not in self.total.keys():
                            self.total[fullDate] = 0
                        self.total[fullDate] += 1
                        self.grandTotal += 1
                        self.addDocument(documents[year][month][day][link])
        return
                                  
    def addDocument(self, document):
        if 'topics' not in document.keys():
            return
        wordKeys = []
        for word in document['topics']:
            wordKeys.append(word)
            if word not in self.pureWords.keys():
                self.pureWords[word] = document['topics'][word]['pure_word']
                self.blockCounts[word] = 0
                self.wordDocuments[word] = []
            self.blockCounts[word] += 1
            self.wordDocuments[word].append(document['url'])
        
        if len(wordKeys):
            self.documents.append(wordKeys)
        return 
    
    
    
    
    