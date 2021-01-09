import json
from .core import Core
from .base import Base
import os

class Txt(Base):
    
    def read(self, filePath):
        file = Core(filePath)
        if file.exists():
            return file.read()
        return None

    def write(self, filePath, data):
        file = Core(filePath)
        if file.exists():
            file.remove()
        file.write(data)
        return
