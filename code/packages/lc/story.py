import math, os
from .core import Core
from file.json import Json as JsonFile

class Story(Core):
    
    def getAnalyzedWords(self):
        self.loadAnalyzedWords()
        return self.data['story_words']

    def loadAnalyzedWords(self):
        pwfWords = self.sort('position_weight_forward')
        pwbWords = self.sort('position_weight_backward')
        
        if not len(pwfWords) or not len(pwbWords):
            return
        
        analyzedKeys = self.data['story_words_keys']
        analyzedKeys = self.getKeys(pwfWords, analyzedKeys, 'position_weight_forward')
        
        for wordKey in pwfWords.keys():
            word = pwfWords[wordKey]
            if ((len(word['blocks']) >= math.floor(self.splits / 2)) and (wordKey not in analyzedKeys)):
                analyzedKeys.append(wordKey)
        
        analyzedKeys = self.getKeys(pwbWords, analyzedKeys, 'position_weight_backward')
        self.data['story_words_keys'] = analyzedKeys
        
        for key in analyzedKeys:
            word = self.data['wordsInfo'][key]
            self.data['story_words'].append(word)
            if word['type'] in ['NNP', 'NNPS']:
                display = word['pure_word'][0].upper() + word['pure_word'][1:]
                    
        self.data['total_story_words'] = len(self.data['story_words'])
        return
    
    def getKeys(self, words, wordKeys, key = 'position_weight_forward', minItems = 10, minWeights = 2):
        initCount = len(wordKeys)
        for wordKey in words.keys():
            if (len(wordKeys) > initCount + minItems):
                break
            
            if wordKey not in wordKeys:
                wordKeys.append(wordKey)
                
        return wordKeys
     
    def _addWordInfo(self, word, type, currentPositionValue):
        if (type not in self.allowedPOSTypes) or (len(word) <= self.minCharLength):
            # print(word, '    ', type)
            return None

        if word in self.stopWords:
            return None
        wordLower = word.lower()
        cleanedWord = self._cleanWord(wordLower)
        if not cleanedWord:
            return None
        wordKey = self.stemmer.stem(cleanedWord)
        localWordInfo = {}
        localWordInfo['type'] = type
        localWordInfo['pure_word'] = cleanedWord
        localWordInfo['stemmed_word'] = wordKey
        localWordInfo['sentiment'] = ''
        
        blockNumber = (currentPositionValue // self.data['threshold'])
        
        if localWordInfo['stemmed_word'] in self.data['wordsInfo'].keys():
            localWordInfo = self.data['wordsInfo'][wordKey]
            localWordInfo['count'] += 1
            localWordInfo['position_weight_backward'] = ((self.data['total_sentences'] - currentPositionValue) / self.data['total_sentences']) * 100
            
            if blockNumber not in localWordInfo['blocks']:
                localWordInfo['blocks'].append(blockNumber)
                
            if len(localWordInfo['blocks']) == self.splits:
                if wordKey not in self.data['story_words_keys']:
                    self.data['story_words_keys'].append(wordKey)
                    self.data['story_about'].append(localWordInfo['pure_word'])
                
            self.data['wordsInfo'][wordKey] = localWordInfo
            return wordKey
        
        
        localWordInfo['blocks'] = [blockNumber]
        localWordInfo['first_block'] = blockNumber
        localWordInfo['category'] = ''
        localWordInfo['description'] = ''
        
        isProperNoun = False
        localWordInfo['pos_type'] = 'Noun'
        if (type in ['NNP', 'NNPS']):
            if (wordLower not in self.properNouns.keys()):
                return 
            
            localWordInfo['pure_word'] = self.properNouns[wordLower]
            isProperNoun = True
            localWordInfo['pos_type'] = 'Proper Noun'
            details = self.__getMoreDetails(wordKey, localWordInfo['pure_word'])
            if details:
                localWordInfo['category'] = details['category']
                localWordInfo['description'] = details['description']
                # print(localWordInfo)
        elif (type in self.wordPosGroups['verb']):
            localWordInfo['pos_type'] = 'Verb'

        localWordInfo['index'] = len(self.data['wordsInfo'])
        localWordInfo['position_weight_forward'] = (currentPositionValue / self.data['total_sentences']) * 100
        localWordInfo['position_weight_backward'] = ((self.data['total_sentences'] - currentPositionValue) / self.data['total_sentences']) * 100
        localWordInfo['count'] = 1
                
        if localWordInfo['stemmed_word'] in self.positiveWords:
            localWordInfo['sentiment'] = 'positive'

        if localWordInfo['stemmed_word'] in self.negativeWords:
            localWordInfo['sentiment'] = 'negative'

        self.data['wordsInfo'][wordKey] = localWordInfo
        # print(localWordInfo)
        # print('------------------------------')
        return wordKey
     
    def __reset(self, text):
        self.knowledgeGraphProcessor.reset()
        super().__reset()
        self.data = {
            'total_words': 0,
            'total_sentences': 0,
            'threshold': 0,
            'total_story_words': 0,
            'story_about': [],
            'story_words_keys': [],
            'proper_nouns': [],
            'story_words': [],
            'wordsInfo': {}
        }
        return
    
    def __getMoreDetails(self, wordKey, pureWord):
        file = JsonFile()
        filePath = os.path.join(self.writer.getWordDirectoryPath(), wordKey + '.json')
        currentInfo = file.read(filePath)
        
        if currentInfo and 'category' in currentInfo.keys():
            return {
                'category': currentInfo['category'],
                'description': currentInfo['description']
            };
        
        category = self.category.get(pureWord)
        if category:
            return {
                'category': category,
                'description': ''
            };
        return self.knowledgeGraph.getMoreDetails(wordKey, pureWord)
    
