import pickle as pk
from .base import Base
from .core import Core as File
import os

class Pickle(Base):

    def read(self, filePath):
        file = File(filePath)
        if file.exists():
            return pk.load(open(filePath, 'rb'));
        return None

    def write(self, filePath, model):
        file = File(filePath)
        if file.exists():
            file.remove()
        pk.dump(model, open(filePath, 'wb'))
        return
