import os, datetime, operator
from reader.analysis import Analysis
from file.json import Json as JsonFile

class Core:
    
    def __init__(self, params):
        self.params = params
        self.rcAnalysis = Analysis()
        self.documentLimit = 100
        self.subTopicDocumentLimit = 2
        self.storyWordPerCategoryLimit = 5
        self.blockOccuranceFactor = 10
        self.termsPerBubble = 3
        self.topics = params['topic_keys']
        self.topicNames = {}
        self.documents = {}
        self.datedCount = {}
        self.terms = {}
        self.total = 0
        self.maxDate = None
        self.minDate = None
        self.totalDaysBetweenMaxMin = 0
        self.usedTerms = {}
        self.intendedTerms = {
            'who': {},
            'where': {},
            'what_topic': {},
            'what_action': {},
            'why_positive': {},
            'why_negative': {}
        }
        self.file = JsonFile()
        self.load()
        return
    
    def get(self):
        if not len(self.documents.keys()):
            return {}
        self.totalDaysBetweenMaxMin = self.daysBetween(self.maxDate, self.minDate)
        self.usedTerms['topics'] = []
        self.usedTerms['actions'] = []
        self.usedTerms['positive'] = []
        self.usedTerms['negative'] = []
        
        whoSamples = self.file.read(os.path.abspath(__file__ + "/../../resources/Who.json"))
        whereSamples = self.file.read(os.path.abspath(__file__ + "/../../resources/Location.json"))

        self.scoreTerms('topics', 'who', ['Person', 'Organization'], whoSamples)
        self.scoreTerms('topics', 'where', ['Location'], whereSamples)
        self.scoreTerms('topics', 'what_topic')
        self.scoreTerms('actions', 'what_action')
        self.scoreTerms('positive', 'why_positive')
        self.scoreTerms('negative', 'why_negative')

        return {
            'description': self.getBoardDescription(),
            'total': self.total,
            'date_range': {
                'min': self.dateToStr(self.minDate),
                'max': self.dateToStr(self.maxDate)
            },
            'when': self.getWhen(),
            'board': self.intendedTerms,
            'documents': self.processDocumentsForDisplay()
        }
        
    def getBoardDescription(self):
        text = 'Displaying ' + str(self.total) + ' news from ' + self.dateToStr(self.minDate) + ' to ' + self.dateToStr(self.maxDate) + ' about '
        totalNames = len(self.topicNames.keys())
        processed = 0
        divider = ''
        for nameKey in self.topicNames.keys():
            if processed <= totalNames - 1:
                text += divider + '"' + self.topicNames[nameKey] + '"'
                processed += 1
            divider = ' and ' if processed == totalNames - 1 else ', '
            
        return text
    
    def scoreTerms(self, fieldKey, destinationKey, categories = None, samples = []):
        if ((fieldKey not in self.terms.keys())
            or not len(self.terms[fieldKey].keys())):
            return []
        
        filterWords = {}
        for term in self.terms[fieldKey].keys():
            word = self.terms[fieldKey][term]
            if categories and (word['category'] not in categories):
                if not len(samples) or (word['pure_word'] not in samples):
                    continue
            word['old_to_new'] = self.getOldToNewScore(self.terms[fieldKey][term]['dates'])
            word['new_to_old'] = self.getNewToOldScore(self.terms[fieldKey][term]['dates'])
            word['consistent'] = (self.terms[fieldKey][term]['old_to_new'] + self.terms[fieldKey][term]['new_to_old']) / 2
            filterWords[term] = word
            
        if not len(filterWords.keys()):
            return   
        self.intendedTerms[destinationKey]['consistent'] = self.fillBoardTerms(filterWords, 'consistent', fieldKey)
        self.intendedTerms[destinationKey]['old_to_new'] = self.fillBoardTerms(filterWords, 'old_to_new', fieldKey)
        self.intendedTerms[destinationKey]['new_to_old'] = self.fillBoardTerms(filterWords, 'new_to_old', fieldKey)
        return
    
    def fillBoardTerms(self, items, attributeKey, fieldKey):
        sorted =  self.sort(items, attributeKey, True) 
        bubbleItems = []
        for item in sorted:
            if item['stemmed_word'] in self.usedTerms[fieldKey]:
                continue
            bubbleItems.append({
                'name': item['pure_word'][0].upper() + item['pure_word'][1:],
                'key': item['stemmed_word'],
                'size': item['block_count'],
                'old_to_new': item['old_to_new'],
                'new_to_old': item['new_to_old'],
                'consistent': item['consistent'],
                'description': item['description']
            })
            self.usedTerms[fieldKey].append(item['stemmed_word'])
            if len(bubbleItems) == self.termsPerBubble:
                break
        return bubbleItems
    
    def getOldToNewScore(self, dates):
        score = 0
        for date in dates:
            score += self.totalDaysBetweenMaxMin - self.daysBetween(self.strToDate(date), self.minDate)
        return score
    
    def getNewToOldScore(self, dates):
        score = 0
        for date in dates:
            score += self.totalDaysBetweenMaxMin - self.daysBetween(self.maxDate, self.strToDate(date))
        return score
    
    def getWhen(self):
        if not len(self.datedCount.keys()):
            return []
        
        data = []
        days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for year in range(self.minDate.year, self.maxDate.year + 1):
            for month in range(1, 12 + 1):
                if (((year == self.minDate.year) and (month < self.minDate.month)) or 
                    ((year == self.maxDate.year) and (month > self.maxDate.month))):
                    continue
                
                totalDays = days[month]
                if self.isLeapYear(year) and (month == 2):
                    days = 29
                for day in range(1, totalDays + 1):
                    if (((year == self.minDate.year) and (month == self.minDate.month) and (day < self.minDate.day)) or 
                        ((year == self.maxDate.year) and (month == self.maxDate.month) and (day > self.maxDate.day))):
                        continue

                    fullDateKey = str(year) + '-' + self.getFormattedMonthOrDay(str(month)) + '-' + self.getFormattedMonthOrDay(str(day))

                    totalCount = 0
                    if fullDateKey in self.datedCount.keys():
                        totalCount = self.datedCount[fullDateKey]

                    data.append({
                        'date': fullDateKey,
                        'value': totalCount
                    })
                    
        return data
    
    def isLeapYear(self, year):
        if (year % 4) == 0:
            if (year % 100) == 0:
                if (year % 400) == 0:
                    return True
                else:
                    return False
            else:
                return True
        return False
    
    def load(self):
        if not self.topics or not len(self.topics):
            return
        
        for key in self.topics:
            data = self.rcAnalysis.getRcFileContent(key)
            if data:
                break
            
        if data:
            self.loadDocuments(data)
            
        return
    
    def loadDocuments(self, data):
        if not data or 'documents' not in data.keys():
            return
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
                    fullDateKey = year + '-' + self.getFormattedMonthOrDay(month) + '-' + self.getFormattedMonthOrDay(day)
                    totalMatch = 0
                    
                    for link in data['documents'][year][month][day].keys():
                        if link in self.documents.keys():
                            continue
                        if self.processSingleDocument(fullDateKey, link, data['documents'][year][month][day][link]) > 0:
                            totalMatch += 1
                            self.total += 1
                    
                    if totalMatch > 0:
                        self.datedCount[fullDateKey]= totalMatch
        return
    
    def processSingleDocument(self, fullDate, link, document):
        score = self.getDocumentTopicScore(document)
        if score == 0:
            return 0
        
        fullDateObject = self.strToDate(fullDate)
        self.setMaxDate(fullDateObject)
        self.setMinDate(fullDateObject)
        self.documents[link] = document
        self.documents[link]['score'] = score
        self.documents[link]['date_key'] = fullDate
        self.addTerms(self.documents[link], fullDate, 'topics')
        self.addTerms(self.documents[link], fullDate, 'actions')
        self.addTerms(self.documents[link], fullDate, 'positive')
        self.addTerms(self.documents[link], fullDate, 'negative')
        return score
        
    def getDocumentTopicScore(self, document):
        shouldMatched = len(self.topics)
        documentTopics = document['topics'].keys()

        if not len(documentTopics) or not shouldMatched:
            return 0
        
        totalMatched = 0
        score = 0
        for topic in self.topics:
            if topic in documentTopics:
                self.topicNames[topic] = document['topics'][topic]['pure_word']
                totalMatched += 1
                score += len(document['topics'][topic]['blocks']) * self.blockOccuranceFactor + document['topics'][topic]['count']
                
        if shouldMatched != totalMatched:
            return 0
        return score / shouldMatched
    
    def addTerms(self, document, date, fieldKey):
        documentTopics = document[fieldKey].keys()
        if not len(documentTopics):
            return 0
        if fieldKey not in self.terms.keys():
            self.terms[fieldKey] = {}
        
        for key in documentTopics:
            self.addTerm(document, date, key, fieldKey)
            
    def addTerm(self, document, date, key, fieldKey):
        if key in self.terms[fieldKey].keys():
            self.terms[fieldKey][key]["block_count"] += 1
            self.terms[fieldKey][key]['dates'].append(date)
            return

        self.terms[fieldKey][key] = document[fieldKey][key]
        self.terms[fieldKey][key]['dates'] = [date]
        self.terms[fieldKey][key]["block_count"] = 1
        
        return
    
    def processDocumentsForDisplay(self):
        if not len(self.documents):
            return []
        
        processedDocuments = {}
        
        for link in self.documents.keys():
            document = self.documents[link]
            processedDocuments[link] = {
                "url": document["url"],
                "title": document["title"],
                "description": document["description"],
                "score": document["score"],
                "date": document["date_key"]
            }
            
        order = self.params['order'] if 'order' in self.params.keys() else 'score'
        direction = self.params['direction'] if 'direction' in self.params.keys() else 'desc'
        booleanDirection = True if direction == 'desc' else False
        
        return self.sort(processedDocuments, order, booleanDirection)
    
    def getFormattedMonthOrDay(self, number):
        if int(number) < 10:
            return '0' + number
        return number
    
    def sort(self, items, attribute='score', reverse=True):
        if not len(items.keys()):
            return []

        sortedTopics = []
        contributors = items.values()
        
        for value in sorted(contributors, key=operator.itemgetter(attribute), reverse=reverse):
            sortedTopics.append(value)

        return sortedTopics
    
    def setMinDate(self, date):
        if not self.minDate or (date < self.minDate):
            self.minDate = date
        return 
    
    def setMaxDate(self, date):
        if not self.maxDate or (date > self.maxDate):
            self.maxDate = date
        return 
    
    def strToDate(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%d')
    
    def dateToStr(self, date):
        return str(date.year) + '-' + self.getFormattedMonthOrDay(str(date.month)) + '-' + self.getFormattedMonthOrDay(str(date.day))
    
    def daysBetween(self, date1, date2):
        return abs((date1 - date2).days)
