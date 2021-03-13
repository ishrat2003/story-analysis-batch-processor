import os
from .base import Base

class RC(Base):

    def __init__(self, path):
        super().__init__(path)
        self.rcDirectoryPath = os.path.join(path, 'rc_content')
        return
    
    def save(self, fileName, data):
        filePath = self.getFilePath(self.rcDirectoryPath, fileName)
        self.file.write(filePath, data)
        return
