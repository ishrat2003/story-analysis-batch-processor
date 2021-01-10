import os
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
    
    self.splits = int(os.environ['SPLIT'])
    self.file = JsonFile()
    self.reset()
    return
  
  def reset(self):
    self.categories = {}
    self.topics = []
    self.actions = []
    self.positive = []
    self.negative = []
    return
  
  def save(self, documentIdentifier, documentTitle, documentDescription, words, date):
    self.reset()
    document = self.getDocument(words, documentIdentifier, documentTitle, documentDescription)
    
    self.saveWords(documentIdentifier, words, date, document)
    self.saveCategories()
    self.saveGc(date)
    return True
  
  def saveGc(self, date):
    filePath = os.path.join(self.gcDirectoryPath, 'topics.json')
    currentInfo = self.file.read(filePath)
    if not currentInfo:
      currentInfo = {}

    if date.year not in currentInfo.keys():
      currentInfo[date.year] = {}
      
    if date.month not in currentInfo[date.year].keys():
      currentInfo[date.year][date.month] = {}
        
    if date.day not in currentInfo[date.year][date.month].keys():
      currentInfo[date.year][date.month][date.day]  = {}
    
    for topic in self.topics:
      if topic not in currentInfo[date.year][date.month][date.day].keys():
        currentInfo[date.year][date.month][date.day][topic] = 0
      currentInfo[date.year][date.month][date.day][topic] += 1
    
    self.file.write(filePath, currentInfo)
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
    alternativeTopics = []
    for word in words:
      totalBlocks = len(word['blocks'])

      if ((totalBlocks == self.splits) and (word['pos_type'] == 'Noun') and (word['stemmed_word'] not in self.topics)):
        self.topics.append(word['stemmed_word'])
      
      if ((totalBlocks > allowedBlocks) and (word['pos_type'] == 'Noun') and (word['stemmed_word'] not in self.topics)):
        alternativeTopics.append(word['stemmed_word'])   
          
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
