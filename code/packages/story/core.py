import operator, math, datetime, os
from nltk import word_tokenize, pos_tag
from nltk.stem.porter import PorterStemmer
from utility.utility import Utility
import regex as re
from .knowledge_graph import KnowledgeGraph
from .category import Category
from file.json import Json as JsonFile
class Core:
    
    def __init__(self, resourcePath):
        self.splits = int(os.environ['SPLIT'])
        self.minCharLength = int(os.environ['MIN_CHAR_LENGTH'])
        self.stopWords = Utility.getStopWords()
        self.positiveWords = Utility.getPositiveWords()
        self.negativeWords = Utility.getNegativeWords()
        self.designations = Utility.getDesignations()
        self.punctuationTypes = ['.', '?', '!']
        self.stemmer = PorterStemmer()
        self.__loadGroups()
        self.knowledgeGraphProcessor = KnowledgeGraph(resourcePath)
        self.category = Category(resourcePath)
        self.resourcePath = resourcePath
        self.maxWordLength = 30
        return
    
    
    def getContextualWords(self, text):
        self.__reset(text)
        self.setProspectiveProperNouns()
        self.setSentences()
        return self.getAnalyzedWords()

    def sort(self, attribute='count'):
        if not len(self.data['wordsInfo'].keys()):
            return

        sortedWords = {}
        contributors = self.data['wordsInfo'].values()

        for value in sorted(contributors, key=operator.itemgetter(attribute, 'count'), reverse=True):
            sortedWords[value['stemmed_word']] = value

        return sortedWords
    
    def setSentences(self):
        sentences = self.__getRawSentences(self.text)
        self.data['total_sentences'] = len(sentences)
        self.data['threshold'] = math.ceil(self.data['total_sentences'] / self.splits)
        currentPositionValue = self.data['total_sentences']
        self.data['total_words'] += self.__getTotalWords()
        
        for sentence in sentences:
            if not sentence: 
                continue
            
            words = self.__getWords(sentence)
            
            for word in words:
                (word, type) = word
                addedWordKey = self._addWordInfo(word, type, currentPositionValue)
            
            currentPositionValue -= 1
            
        return
    
    def setProspectiveProperNouns(self):
        if len(self.properNouns.keys()):
            return
        
        items = re.finditer('([A-Z][a-z0-9\-]+\s*)+(of\s[A-Z][a-z0-9\-]+)*', self.text)

        if not items:
            return
        
        for item in items:
            words = item.group(0).split(' ')
            properNoun = []
            for word in words:
                word = word.strip()
                lowerWord = word.lower()
                if lowerWord in self.stopWords or not word:
                    continue
                properNoun.append(word)
            
            if properNoun:
                fullProperNoun = self._cleanWord(' '.join(properNoun))
                indexNoun = self.stemmer.stem(properNoun[-1].lower())
                if indexNoun in self.properNouns.keys():
                  continue
                else:
                    self.properNouns[indexNoun] = self.removeDesignation(fullProperNoun)
        return
    
    def removeDesignation(self, fullName):
        possibleNames = [fullName.title()]
        for item in self.designations:
            if len(item) > len(fullName):
                return possibleNames[-1]
            if fullName.find(item) != -1:
                if item not in self.properNouns.keys():
                    self.properNouns[item] = item.title()
                possibleNames.append(fullName.replace(item, "").title())

        return possibleNames[-1]
    
    def _addWordInfo(self, word, type, currentPositionValue):
        if (type not in self.allowedPOSTypes) or (len(word) <= self.minCharLength):
            # print(word, '    ', type)
            return None

        if word in self.stopWords:
            return None
        wordLower = word.lower()
        cleanedWord = self._cleanWord(wordLower)
        if not cleanedWord or len(cleanedWord) > self.maxWordLength:
            return None
        
        wordKey = self.stemmer.stem(cleanedWord)
        localWordInfo = {}
        localWordInfo['type'] = type
        localWordInfo['pure_word'] = cleanedWord.title()
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
                    
            localWordInfo['score'] = self._getScore(localWordInfo)
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
            # print(wordKey, '--', localWordInfo['category'])
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

        localWordInfo['score'] = self._getScore(localWordInfo)
        self.data['wordsInfo'][wordKey] = localWordInfo
        return wordKey
    
    
    def _getScore(self, word):
        return word['count']
    
    def _cleanWord(self, word):
        word = word.lower()
        word = re.sub(r'([A-Za-z0-9\-\.]+)\'s', r'\1', word)
        word = re.sub(r'([A-Za-z0-9\-\.]+)s\'', r'\1', word)
        return re.sub(r'[^A-Za-z0-9\.\-\&\s]+', r'', word)
    
    def __getWords(self, text):
        words = word_tokenize(text)
        return pos_tag(words)
    
    def __getRawSentences(self, text):
        text = re.sub(r'([0-9]+)\.([0-9]+)', r'\1##\2', text)
        text = re.sub(r'\.', r'#END#', text)
        text = re.sub(r'([0-9]+)##([0-9]+)', r'\1.\2', text)
        text = re.sub(r'[\/|\\]', r' ', text)
        text = re.split("\n|#END#|!|\?", text)
        return list(filter(lambda sentence: len(sentence) > 0, text))
    
    def __getCount(self, value):
        list = re.findall('\s' + value, self.text, flags=re.IGNORECASE)
        return len(list)
    
    def __getTotalWords(self):
        list = re.findall("(\S+)", self.text)
        # Return length of resulting list.
        return len(list)
     
    def __reset(self, text):
        self.text = text
        self.properNouns = {}
        self.knowledgeGraphProcessor.reset()
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
        filePath = os.path.join(self.resourcePath, 'words', wordKey + '.json')
        currentInfo = file.read(filePath)
        
        category = self.category.get(pureWord)
        if category:
            return {
                'category': category,
                'description': ''
            };
        
        if currentInfo and 'category' in currentInfo.keys():
            return {
                'category': currentInfo['category'],
                'description': currentInfo['description']
            };
        
        return self.knowledgeGraphProcessor.getMoreDetails(wordKey, pureWord)
    
    '''
    CC coordinating conjunction
    CD cardinal digit
    DT determiner
    EX existential there (like: “there is” … think of it like “there exists”)
    FW foreign word
    IN preposition/subordinating conjunction
    JJ adjective ‘big’
    JJR adjective, comparative ‘bigger’
    JJS adjective, superlative ‘biggest’
    LS list marker 1)
    MD modal could, will
    NN noun, singular ‘desk’
    NNS noun plural ‘desks’
    NNP proper noun, singular ‘Harrison’
    NNPS proper noun, plural ‘Americans’
    PDT predeterminer ‘all the kids’
    POS possessive ending parent’s
    PRP personal pronoun I, he, she
    PRP$ possessive pronoun my, his, hers
    RB adverb very, silently,
    RBR adverb, comparative better
    RBS adverb, superlative best
    RP particle give up
    TO, to go ‘to’ the store.
    UH interjection, errrrrrrrm
    VB verb, base form take
    VBD verb, past tense took
    VBG verb, gerund/present participle taking
    VBN verb, past participle taken
    VBP verb, sing. present, non-3d take
    VBZ verb, 3rd person sing. present takes
    WDT wh-determiner which
    WP wh-pronoun who, what
    WP$ possessive wh-pronoun whose
    WRB wh-abverb where, when
    '''
    def __loadGroups(self):
        self.wordPosGroups = {}
        self.wordPosGroups['noun'] = ['NN', 'NNS', 'NNP', 'NNPS']
        #self.wordPosGroups['adjective'] = ['JJ', 'JJR', 'JJS']
        #self.wordPosGroups['adverb'] = ['RB', 'RBR', 'RBS']
        self.wordPosGroups['verb'] = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        #self.wordPosGroups['combined'] = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS']
        # self.wordPosGroups['other'] = ['IN', 'TO']
        
        self.allowedPOSTypes = []
        posGroupKeys = self.wordPosGroups.keys()
        if not posGroupKeys:
            return
        
        for key in posGroupKeys:
            self.allowedPOSTypes = list(set(self.allowedPOSTypes + self.wordPosGroups[key]))

        return
