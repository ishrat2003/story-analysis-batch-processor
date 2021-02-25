from .story import Story

class Context:
    
    def __init__(self, loader, writer):
        self.loader = loader
        self.writer = writer
        self.story = Story(self.writer)
        return
    
    def process(self, fileContent):
        data = self.loader.load(fileContent)
        
        if not data:
            return False
        
        data = self.loader.fetchPage(data['link'], data)
        content = self.loader.getContent(data)
        date = self.loader.getDate(data)

        if not content or not date:
            return False
        
        storyWords = self.getWords(content)

        if not len(storyWords):
            return False
        
        documentIdentifier = self.loader.getIdentifier(data)
        documentTitle = self.loader.getTitle(data)
        documentDescription = self.loader.getShortDescription(data)
        
        self.writer.save(documentIdentifier, documentTitle, documentDescription, storyWords, date)
        return True
    
    def getWords(self, content):
        return self.story.getLCWords(content)
    
    