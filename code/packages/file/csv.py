from .base import Base
from .core import Core as File
import os

class Csv(Base):
    
    def read(self, filePath):
        file = File(filePath)
        if file.exists():
            return file.read()
        return None

    def write(self, filePath, data):
        file = File(filePath)
        if file.exists():
            file.remove()
        file.write(data)
        return