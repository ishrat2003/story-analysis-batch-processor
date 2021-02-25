import os
from file.json import Json as JsonFile

class Category:
  def __init__(self, path):
    self.file = JsonFile()
    self.categoryDirectoryPath = os.path.join(path, 'categories')
    return
  
  def get(self, pureWord):
    if self.isSpecifiedCategory(pureWord, 'Location'):
        return 'Location'
    if self.isSpecifiedCategory(pureWord, 'Person'):
        return 'Person'
    if self.isSpecifiedCategory(pureWord, 'Brand'):
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

