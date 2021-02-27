import os, operator, nltk, re, datetime
from filesystem.directory import Directory
from file.json import Json as JsonFile
from nltk.stem.porter import PorterStemmer


class Core:

  def __init__(self, path):
    self.path = path
    self.stemmer = PorterStemmer()
    self.wordDirectoryPath = os.path.join(path, 'words')
    wordDirectory = Directory(self.wordDirectoryPath)
    wordDirectory.create()
    
    self.categoryDirectoryPath = os.path.join(path, 'categories')
    categoryDirectory = Directory(self.categoryDirectoryPath)
    categoryDirectory.create()
    
    self.gcDirectoryPath = os.path.join(path, 'gc')
    gcDirectory = Directory(self.gcDirectoryPath)
    gcDirectory.create()

    self.mapsDirectoryPath = os.path.join(path, 'maps')
    self.countryFilePath = os.path.join(self.gcDirectoryPath, 'country_topics.json')
    self.personFilePath = os.path.join(self.gcDirectoryPath, 'person_topics.json')
    self.organizationFilePath = os.path.join(self.gcDirectoryPath, 'organization_topics.json')
    self.commonDataFilePath = os.path.join(self.gcDirectoryPath, 'common.json')
    self.documentsListFilePath = os.path.join(self.gcDirectoryPath, 'documents.json')
    
    self.splits = int(os.environ['SPLIT'])
    self.file = JsonFile()
    self.reset()
    return
  
  def getPath(self):
    return self.path
  
  def reset(self):
    self.categories = {}
    self.topics = {}
    self.actions = {}
    self.positive = {}
    self.negative = {}
    self.common = {}
    self.loadCountries()
    self.loadPerson()
    self.loadOrganization()
    self.loadCommonData()
    self.loadDocumentsList()
    self.loadShortCountryNames()
    return
  
  def getWordDirectoryPath(self):
    return self.wordDirectoryPath
  
  def save(self, documentIdentifier, documentTitle, documentDescription, words, date):
    self.reset()
    # if documentIdentifier in self.documentsList:
    #   return False
    self.documentsList.append(documentIdentifier)
    self.updateCommon(date)
    
    document = self.getDocument(words, documentIdentifier, documentTitle, documentDescription)
    
    self.saveWords(documentIdentifier, words, date, document)
    self.saveCategories()
    self.saveGc(date)
    return True
  
  def saveGc(self, date):
    filePath = os.path.join(self.gcDirectoryPath, 'topics.json')
    
    yearKey = str(date.year)
    monthKey = str(date.month)
    dayKey = str(date.day)
    # print("-------------------------------")
    currentInfo = self.file.read(filePath)
    # if(currentInfo):
    #   print('current info', currentInfo)
    #   print(currentInfo.keys())

    if not currentInfo:
      currentInfo = {}   
    
    if yearKey not in currentInfo.keys():
      currentInfo[yearKey] = {}
      
    # print(currentInfo[yearKey].keys())
    if monthKey not in currentInfo[yearKey].keys():
      currentInfo[yearKey][monthKey] = {}
      
    # print(currentInfo[yearKey][monthKey].keys())  
    if dayKey not in currentInfo[yearKey][monthKey].keys():
      currentInfo[yearKey][monthKey][dayKey]  = {}
    
    # print(currentInfo[yearKey][monthKey][dayKey])
    for topicKey in self.topics.keys():
      # print(topic, ' ', yearKey, ' ', monthKey, '  ', dayKey)
      # print(currentInfo[yearKey][monthKey][dayKey].keys())
      if topicKey not in currentInfo[yearKey][monthKey][dayKey].keys():
        currentInfo[yearKey][monthKey][dayKey][topicKey] = {
          'block_count': 0,
          'display': self.topics[topicKey]['pure_word'],
          'category': self.topics[topicKey]['category'], 
          'description': self.topics[topicKey]['description'],
          'sentiment': self.topics[topicKey]['sentiment']
        }
      currentInfo[yearKey][monthKey][dayKey][topicKey]['block_count'] += 1
    # print(currentInfo)
    self.file.write(filePath, currentInfo)
    self.file.write(self.countryFilePath, self.countries)
    self.file.write(self.personFilePath, self.person)
    self.file.write(self.organizationFilePath, self.organization)
    self.file.write(self.commonDataFilePath, self.common)
    self.file.write(self.documentsListFilePath, self.documentsList)
    # print(self.file.read(filePath))
    return
  
  def saveCategories(self):
    for category in self.categories.keys():
      if not category:
        continue
      filePath = os.path.join(self.categoryDirectoryPath, category + '.json')
      currentList = self.file.read(filePath)
      if not currentList:
        currentList = []
      for pureWord in self.categories[category]:
        if pureWord not in currentList:
          currentList.append(pureWord)
      
      self.file.write(filePath, currentList)
    return

  def getDocument(self, words, url, title, description):
    if not words:
      return False

    allowedBlocks = (self.splits / 2)
    alternativeTopics = {}
    orderedTopics = {}
    for word in words:
      totalBlocks = len(word['blocks'])
      
      if ((word['pos_type'] == 'Noun') and (word['stemmed_word'] not in self.topics.keys())):
        # if (totalBlocks == self.splits):
        #   self.topics[word['stemmed_word']] = word
        if (totalBlocks > allowedBlocks):
          alternativeTopics[word['stemmed_word']] = word
        # if (len(orderedTopics) <= 3):
        #   orderedTopics[word['stemmed_word']] = word
          
      if ((totalBlocks > allowedBlocks) and (word['pos_type'] == 'Verb') and (word['stemmed_word'] not in self.actions)):
        self.actions[word['stemmed_word']] = word
      
      if ((word['sentiment'] == 'positive') and (word['stemmed_word'] not in self.positive)):
        self.positive[word['stemmed_word']] = word
        
      if ((word['sentiment'] == 'negative') and (word['stemmed_word'] not in self.negative)):
        self.negative[word['stemmed_word']] = word
      
      if (word['category'] not in self.categories.keys()):
        self.categories[word['category']] = []
      if (word['pure_word'] not in  self.categories[word['category']]):
        self.categories[word['category']].append(word['pure_word'])
        
    if not len(self.topics):
      self.topics = alternativeTopics
        
    if not len(self.topics):
        self.topics = orderedTopics
    return {
      'url': url,
      'title': title,
      'description': description,
      'category': word['category'],
      'blocks': word['blocks'],
      'first_block': word['first_block'],
      'position_weight_forward': word['position_weight_forward'],
      'position_weight_backward': word['position_weight_backward'],
      'count': word['count'],
      'topics': self.topics,
      'actions': self.actions,
      'positive': self.positive,
      'negative': self.negative
    }
        
  def saveWords(self, documentIdentifier, words, date, document):
    if not words:
      return False
    
    yearKey = str(date.year)
    monthKey = str(date.month)
    dayKey = str(date.day)
    fullDateKey = yearKey + '-' + self.getFormattedMonthOrDay(monthKey) + '-' + self.getFormattedMonthOrDay(dayKey)
    
    for word in words:
      if word['pos_type'] not in ['Noun', 'Proper Noun']:
        continue
      
      filePath = os.path.join(self.wordDirectoryPath, word['stemmed_word'] + '.json')
      currentInfo = self.file.read(filePath)

      if not currentInfo:
        currentInfo = {
          'type': word['type'], 
          'pure_word': word['pure_word'], 
          'stemmed_word': word['stemmed_word'], 
          'category': word['category'], 
          'description': word['description'], 
          'pos_type': word['pos_type'],
          'sentiment': word['sentiment'],
          'total_blocks': 0,
          'documents': {}
        }
        
      if 'documents' not in currentInfo.keys():
        currentInfo['documents'] = {}
      
      if yearKey not in currentInfo['documents'].keys():
        currentInfo['documents'][yearKey] = {}
      
      if monthKey not in currentInfo['documents'][yearKey].keys():
        currentInfo['documents'][yearKey][monthKey] = {}
        
      if dayKey not in currentInfo['documents'][yearKey][monthKey].keys():
        currentInfo['documents'][yearKey][monthKey][dayKey]  = {}
      
      if documentIdentifier not in currentInfo['documents'][yearKey][monthKey][dayKey].keys():
        if not self.isWordInDocument(document, word['stemmed_word']) and word['pos_type'] != 'Verb':
              document['topics'][word['stemmed_word']] = word
          
        currentInfo['documents'][yearKey][monthKey][dayKey][documentIdentifier] = document
        currentInfo['total_blocks'] += 1
      
      if word['type'] in ['NNP', 'NNPS']:
        countryName = self.getCountyName(word['pure_word'])
        wordKey = word['pure_word'].lower().strip().replace(' ', '_')
        if countryName:
          wordKey = countryName.lower()
          self.countries[wordKey] =  self.updatedItem(word, self.countries, fullDateKey, wordKey)
        elif (word['category'] == 'Person'):
          self.person[wordKey] =  self.updatedItem(word, self.person, fullDateKey, wordKey)
        elif (word['category'] == 'Organization'):
          self.organization[wordKey] =  self.updatedItem(word, self.organization, fullDateKey, wordKey)    

      self.file.write(filePath, currentInfo)
    return True
  
  def isWordInDocument(self, document, wordKey):
    if wordKey in document['topics'].keys():
      return True
    if wordKey in document['actions'].keys():
      return True
    return False
  
  def updatedItem(self, word, items, fullDateKey, wordKey):
    wordKey = wordKey.lower().strip()
    processedWord = None
    if wordKey not in items.keys():
      processedWord = {
        'display': word['pure_word'],
        'total_block_count': 0,
        'count_per_day': {},
        'key': word['stemmed_word']
      }
    else:
      processedWord = items[wordKey]
    if fullDateKey not in processedWord['count_per_day'].keys():
      processedWord['count_per_day'][fullDateKey] = 0
      
    processedWord['count_per_day'][fullDateKey] += 1 
    processedWord['total_block_count'] += 1
    return processedWord
        
  
  def sort(self, items, attribute='block_count'):
    if not len(items):
      return []

    sortedItems = []
    contributors = items.values()
    
    for value in sorted(contributors, key=operator.itemgetter(attribute, 'block_count'), reverse=True):
        sortedItems.append(value)

    return sortedItems
  
  def loadCountries(self):
    self.countries = self.file.read(self.countryFilePath)
    
    if self.countries and len(self.countries.keys()):
      return
    
    filePath = os.path.join(self.mapsDirectoryPath, 'countries.json')
    items = self.file.read(filePath)
    
    self.countries = {}
    for item in items:
      self.countries[item['name'].lower()] = {
        'id': item['id'],
        'display': item['name'],
        'total_block_count': 0,
        'key': self.getKey(item['name']),
        'count_per_day': {}
      }
    return
  
  def loadShortCountryNames(self):
    shortfilePath = os.path.join(self.mapsDirectoryPath, 'short_name_countries.json')
    self.shortCountryNames = self.file.read(shortfilePath)
    return
  
  def getKey(self, word):
    keys = word.split(' ')
    key = keys[-1]
    return self.stemmer.stem(key.lower())
  
  def loadPerson(self):
    self.person = self.file.read(self.personFilePath)
    if self.person and len(self.person.keys()):
      return
    self.person = {}
    return
  
  def loadOrganization(self):
    self.organization = self.file.read(self.organizationFilePath)
    if self.organization and len(self.organization.keys()):
      return
    self.organization = {}
    return
  
  def loadCommonData(self):
    self.common = self.file.read(self.commonDataFilePath)
    if self.common and len(self.common.keys()):
      return
    self.common = {
      'total': 0,
      'max_date': '',
      'min_date': '',
    }
    return
  
  def loadDocumentsList(self):
    self.documentsList = self.file.read(self.documentsListFilePath)
    if self.documentsList and len(self.documentsList):
      return
    self.documentsList = []
    return
  
  def getCountyName(self, name):
    name = name.lower()
    if name in self.countries.keys():
      return name
    if name in self.shortCountryNames.keys():
      return self.shortCountryNames[name]
    return None
  
  def updateCommon(self, date):
    self.common['total'] += 1
    
    if self.shouldResetMaxDate(date):
      self.common['max_date'] = date.strftime("%Y-%m-%d")
      
    if self.shouldResetMinDate(date):
      self.common['min_date'] = date.strftime("%Y-%m-%d")
    return
  
  
  def isGreaterThanMin(self, date):
        date = self.strToDate(date)
        minDate = self.strToDate(self.dataDates['min'])
        return date > minDate
    
  def shouldResetMaxDate(self, date):
      if not self.common['max_date']:
        return True
      date = self.strToDate(date.strftime("%Y-%m-%d"))
      maxDate = self.strToDate(self.common['max_date'])
      return maxDate < date
    
  def shouldResetMinDate(self, date):
      if not self.common['min_date']:
        return True
      date = self.strToDate(date.strftime("%Y-%m-%d"))
      minDate = self.strToDate(self.common['min_date'])
      return minDate > date
  
  def strToDate(self, date):
      return datetime.datetime.strptime(date, '%Y-%m-%d')
    
  def getFormattedMonthOrDay(self, number):
      if int(number) < 10:
        return '0' + number
      return number
  
  def _cleanWord(self, word):
    word = word.strip()
    word = re.sub(r'\s+', r'_', word)
    return re.sub(r'[\'|\/]+', r'', word)
        
    

