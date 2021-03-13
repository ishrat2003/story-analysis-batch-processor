from nltk import word_tokenize, pos_tag
from nltk.stem.porter import PorterStemmer
import regex as re
import sys

class Scanner:
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        return
    
    def scan(self, text, wordKey, referenceWords):
        self.sentenceWords = {}
        self.loadRelationsMatchingSentences(text, wordKey, referenceWords)
        return self.sentenceWords
    
    def loadRelationsMatchingSentences(self, text, wordKey, referenceWords):
        
        items = re.finditer('[^!\?\.\n]*' + wordKey + '[^!\?\.\n]*[!\.\?\n]', text.lower())
        for item in items:
            self.loadSecondaryLevelWords(item.group(0), wordKey, referenceWords)
        return items
    
    
    def loadSecondaryLevelWords(self, sentence, currentWordKey, referenceWords):
        allowedPOSTypes = ['NN', 'NNS', 'NNP', 'NNPS']
        sentence = re.sub(r'[^0-9a-z\s]+', r' ', sentence)
        sentence = re.sub(r'\s+', r' ', sentence)
        words = pos_tag(word_tokenize(sentence))
        
        
        for word in words:
            (wordDisplay, type) = word
            wordKey = self.stemmer.stem(wordDisplay)
            if (type not in allowedPOSTypes) or (wordKey not in referenceWords) or (wordKey == currentWordKey):
                continue
            
            if wordKey not in self.sentenceWords.keys():
                self.sentenceWords[wordKey] = {
                    'display': wordDisplay[0].upper() + wordDisplay[1:],
                    'value': 0
                }
                self.sentenceWords[wordKey]['value'] += 1
            
        return 