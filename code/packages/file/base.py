from .core import Core
import os

class Base:
    
    def remove(self, filePath):
        file = Core(filePath)
        return file.remove()
    
    def getFile(self, filename, writeHeader = True, path = None):
        if not path:
            path = self.path
        path = os.path.join(path, filename)
        file = Core(path, writeHeader)
        return file
    
    def getFilePath(self, fileName, path):
        return Core.join(path, fileName)

