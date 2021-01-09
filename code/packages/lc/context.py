from .story import Story

class Context:
    
    def __init__(self, loader, writer):
        self.loader = loader
        self.writer = writer
        self.story = Story()
        return
    
    def process(self, fileContent):
        data = self.loader.load(fileContent)
        if not data:
            return False
        
        content = self.loader.getContent(data)
        date = self.loader.getDate(data)

        if not content or not date:
            return False
        
        storyWords = self.getWords(content)
        
        if not len(storyWords):
            return False
        
        return self.writer.save(self.loader.getIdentifier(data), storyWords, date)
    
    def getWords(self, content):
        return self.story.getLCWords(content)
    
    