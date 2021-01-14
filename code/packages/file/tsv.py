import pandas as pd
import os, sys
from .base import Base

class Tsv(Base):
    
    def read(self, filePath): 
        return pd.read_csv(filePath, sep='\t')

