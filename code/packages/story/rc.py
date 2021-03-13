import math, os, sys
from .core import Core
from .scanner import Scanner

class RCStory(Core):
    
    def __init__(self, path):
        super().__init__(path)
        self.positionContributingFactor = 0.5
        self.occuranceContributingFactor = 1
        self.filterRate = 0.7
        self.maxScore = 0
        self.scanner = Scanner()
        return
    
    def getAnalyzedWords(self):
        self.loadAnalyzedWords()
        return self.data['story_words']

    def loadAnalyzedWords(self):
        sortedWords = self.sort('score')
        if not sortedWords:
            return
        
        minAllowedWeight = self.maxScore * self.filterRate
        filteredWords = self.getFilteredWords(sortedWords, minAllowedWeight)
        if not filteredWords:
            return
        self.data['story_words'] = {}

        for wordKey in filteredWords.keys():
            self.data['story_words'][wordKey] = self.scanner.scan(self.text, wordKey, filteredWords)
        return
    
    def getFilteredWords(self, sortedWords, minAllowedWeight):
        return dict((key, value) for key, value in sortedWords.items() if value['score'] > minAllowedWeight)
    
    def _getScore(self, word):
        score = word['position_weight_forward'] * self.positionContributingFactor + word['count'] * self.occuranceContributingFactor
        if self.maxScore < score:
            self.maxScore = score
            
        return score
