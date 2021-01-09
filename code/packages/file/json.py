import json
from .base import Base
from .core import Core as File
import os

class Json(Base):
    
    def read(self, filePath):
        file = File(filePath)
        if file.exists():
            with open(filePath, 'r') as jsonFile:
                data = json.load(jsonFile)
                return data
        return None

    def write(self, filePath, data):
        file = File(filePath)
        if file.exists():
            file.remove()
        with open(filePath, 'w') as jsonFile:
            json.dump(data, jsonFile)
        return
