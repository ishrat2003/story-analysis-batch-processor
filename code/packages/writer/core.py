import os, operator
from filesystem.directory import Directory
from file.json import Json as JsonFile

class Core:

  def __init__(self, path):
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
    
    self.splits = int(os.environ['SPLIT'])
    self.file = JsonFile()
    self.loadCountries()
    self.reset()
    return
  
  def reset(self):
    self.categories = {}
    self.topics = {}
    self.actions = []
    self.positive = []
    self.negative = []
    return
  
  def getWordDirectoryPath(self):
    return self.wordDirectoryPath
  
  def save(self, documentIdentifier, documentTitle, documentDescription, words, date):
    self.reset()
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
        
        if self.topics[topicKey]['pure_word'] in self.countries.keys():
          print(self.topics[topicKey]['pure_word'])
          self.countries[self.topics[topicKey]['pure_word']]['block_count'] += 1
          self.countries[self.topics[topicKey]['pure_word']]['key'] = topicKey
        
      currentInfo[yearKey][monthKey][dayKey][topicKey]['block_count'] += 1

    # print(currentInfo)
    self.file.write(filePath, currentInfo)
    self.file.write(self.countryFilePath, self.sort(self.countries))
    
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
        if (totalBlocks == self.splits):
          self.topics[word['stemmed_word']] = word
        if (totalBlocks > allowedBlocks):
          alternativeTopics[word['stemmed_word']] = word
        if (len(orderedTopics) <= 3):
          orderedTopics[word['stemmed_word']] = word
          
      if ((totalBlocks > allowedBlocks) and (word['pos_type'] == 'Verb') and (word['stemmed_word'] not in self.actions)):
        self.actions.append(word['stemmed_word'])
      
      if ((word['sentiment'] == 'positive') and (word['stemmed_word'] not in self.positive)):
        self.positive.append(word['stemmed_word'])
        
      if ((word['sentiment'] == 'negative') and (word['stemmed_word'] not in self.negative)):
        self.negative.append(word['stemmed_word'])
      
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
    
    for word in words:
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
      
      if date.year not in currentInfo['documents'].keys():
        currentInfo['documents'][date.year] = {}
      
      if date.month not in currentInfo['documents'][date.year].keys():
        currentInfo['documents'][date.year][date.month] = {}
        
      if date.day not in currentInfo['documents'][date.year][date.month].keys():
        currentInfo['documents'][date.year][date.month][date.day]  = {}
      
      if documentIdentifier not in currentInfo['documents'][date.year][date.month][date.day].keys():
        currentInfo['documents'][date.year][date.month][date.day][documentIdentifier] = {}
        
      currentInfo['documents'][date.year][date.month][date.day][documentIdentifier] = document
      
      currentInfo['total_blocks'] += 1
      
      self.file.write(filePath, currentInfo)
    return True
  
  def sort(self, items, attribute='block_count'):
    if not len(items):
      return []

    sortedItems = []
    contributors = items.values()
    
    for value in sorted(contributors, key=operator.itemgetter(attribute, 'display'), reverse=True):
        sortedItems.append(value)

    return sortedItems
  
  def loadCountries(self):
    self.countries = self.file.read(self.countryFilePath)
    if self.countries and self.countries.keys().length:
      return
    
    filePath = os.path.join(self.mapsDirectoryPath, 'countries.json')
    items = self.file.read(filePath)
    self.countries = {}
    for item in items:
      self.countries[item['name']] = {
        'id': item['id'],
        'display': item['name'],
        'block_count': 0,
        'key': None
      }
    return
    

