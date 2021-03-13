from nltk import word_tokenize, pos_tag
from nltk.stem.porter import PorterStemmer
import regex as re
import sys

class Scanner:
    
    def scan(self, text, wordKey, referenceWords):
        print(wordKey)
        sentences = self.getMatchingSentences(text, wordKey)
        sys.exit();
        return
    
    def getMatchingSentences(self, text, wordKey):
        print(text)
        items = re.finditer('[^!\?\.\n]*' + wordKey + '[^!\?\.\n]*[!\.\?\n]', text.lower())
        for item in items:
            print(item)
        return items
