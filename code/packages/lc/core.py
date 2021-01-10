import operator, math, datetime
from nltk import word_tokenize, pos_tag
from nltk.stem.porter import PorterStemmer
from utility.utility import Utility
import regex as re
import os
from .knowledge_graph import KnowledgeGraph

class Core:
    
    def __init__(self):
        self.splits = int(os.environ['SPLIT'])
        self.minCharLength = int(os.environ['MIN_CHAR_LENGTH'])
        self.stopWords = Utility.getStopWords()
        self.positiveWords = Utility.getPositiveWords()
        self.negativeWords = Utility.getNegativeWords()
        self.punctuationTypes = ['.', '?', '!']
        self.stemmer = PorterStemmer()
        self.__loadGroups()
        self.knowledgeGraph = KnowledgeGraph()
        return
    
    
    def getLCWords(self, text):
        self.__reset(text)
        self.setProspectiveProperNouns()
        self.setSentences()
        return self.getAnalyzedWords()

   
    def getAnalyzedWords(self):
        return self.data
    

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
        
        items = re.finditer('([A-Z][a-z0-9\-]+\s*)+', self.text)

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
                fullProperNoun = ' '.join(properNoun)
                indexNoun = self.stemmer.stem(properNoun[-1].lower())
                if indexNoun in  self.properNouns.keys():
                  continue
                else:
                    self.properNouns[indexNoun] = fullProperNoun
        return
    
    
    def _cleanWord(self, word):
        return re.sub(r'\'', r'', word)
    
    def __getWords(self, text):
        words = word_tokenize(text)
        return pos_tag(words)
    
    def __getRawSentences(self, text):
        text = re.sub(r'([0-9]+)\.([0-9]+)', r'\1##\2', text)
        text = re.sub(r'\.', r'#END#', text)
        text = re.sub(r'([0-9]+)##([0-9]+)', r'\1.\2', text)
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
