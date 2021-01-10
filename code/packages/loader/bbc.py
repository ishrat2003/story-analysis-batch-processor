import json, datetime
from .core import Core
import urllib
from bs4 import BeautifulSoup

class BBC(Core):
    
    def getDate(self, item):
        return datetime.datetime.strptime(item['pubDate'][5:16], '%d %b %Y')
    
    def getContent(self, item):
        return item['title'] + '. ' + self.getPageContent(item['link'])
    
    def getTitle(self, item):
        return item['title']
    
    def getShortDescription(self, item):
        return item['description']
    
    def getPageContent(self, link):
        fp = urllib.request.urlopen(link)
        mybytes = fp.read()
        page = mybytes.decode("utf8")
        fp.close()
        
       
        soup = BeautifulSoup(page, features="html.parser")
        divs = soup.findAll('div', attrs={"class":"story-body__inner"})
        if divs:
            return self.getDivText(divs)
 
        text = ''
        articles = soup.findAll('article')
        for article in articles:
            for item in article.findChildren():
                if not self.shouldIncludeItem(item):
                    continue
                if item.name in ['div']:
                    text += self.getDivText(item.findChildren())
                elif item.name in ['p', 'ul', 'li', 'ol']:
                    text += str(item.text) + ' '

        return text
    
    def shouldIncludeItem(self, item):
        if item.name not in ['p', 'ul', 'li', 'ol', 'div']:
            return False
        
        if item.attrs and 'class' in item.attrs.keys():
            for cssClass in item.attrs['class']:
                if cssClass.find('RichText') != -1:
                    return True
        
        return False
        
    
    def getDivText(self, divs):
        text = '';
        for div in divs:
            for item in div.findChildren():
                if item.name in ['p', 'ul', 'li', 'ol']:
                    text += str(item.text) + ' '
        return text

    
    