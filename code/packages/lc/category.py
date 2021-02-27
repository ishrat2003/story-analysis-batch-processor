import os
from file.json import Json as JsonFile

class Category:
  def __init__(self, path):
    self.file = JsonFile()
    self.categoryDirectoryPath = os.path.join(path, 'categories')
    return
  
  def get(self, pureWord):
    if self.isSpecifiedCategory(pureWord, 'Location') or self.isLocation(pureWord):
        return 'Location'
    if self.isSpecifiedCategory(pureWord, 'Person') or self.isPerson(pureWord):
        return 'Person'
    if self.isSpecifiedCategory(pureWord, 'Brand') or self.isOrganization(pureWord):
        return 'Organization'
    if self.isSpecifiedCategory(pureWord, 'Organization'):
        return 'Organization'
    return None
       
  def isSpecifiedCategory(self, pureWord, category):
    filePath = os.path.join(self.categoryDirectoryPath, category + '.json')
    items = self.file.read(filePath)
    if items and len(items) and (pureWord in items):
      return True
    return False
  
  def isOrganization(self, text):
      for part in ['company', 'ltd', 'sons', 'tech', 'lab', 'regiment']:
          if self.stringContains(text.lower(), part + ' '):
              return True
          
      return False
  
  def isLocation(self, text):
      for part in ['street', 'region', 'road', 'avenue', 'state', 'county', 'station', 'airport', 'highway', 'city', 'dock', 'port', 'highway']:
          if self.stringContains(text.lower(), part + ' '):
              return True
          
      return False
    
  def isPerson(self, text):
      for title in ['mr', 'mrs', 'miss', 'dr', 'doctor', 'prof', 'professor', 'sir']:
          if self.stringContains(text.lower(), title + ' '):
              return True
          
      return False
    
  def stringContains(self, text, subText):
      if not text or (text.find(subText) == -1):
          return False
      return True

