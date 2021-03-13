import os
from file.json import Json as JsonFile

class Base:

    def __init__(self, path):
        self.path = path
        self.file = JsonFile()
        return
    
    def getPath(self):
        return self.path
    
    def getFilePath(self, dirPath, filename):
        return os.path.join(dirPath, filename + '.json')
        
