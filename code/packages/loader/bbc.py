import json, datetime
from .core import Core

class BBC(Core):
    
    def getDate(self, item):
        print(item['pubDate'])
        return datetime.datetime.strptime(item['pubDate'][5:16], '%d %b %Y')
    
    def getContent(self, item):
        return item['title'] + '.' + item['content']