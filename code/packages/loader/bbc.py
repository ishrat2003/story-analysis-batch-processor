import json, datetime, re
from .core import Core
import urllib, socket
from bs4 import BeautifulSoup
import dateutil.parser as parser

class BBC(Core):
    
    def __init__(self, format = "json"):
        super().__init__()
        self.html = ''
        return
    
    def getDate(self, item):
        if not item or 'pubDate' not in item.keys():
            return ''
        
        return parser.parse(item['pubDate'])
    
    def getContent(self, item):
        if not item or 'content' not in item.keys():
            return ''
        
        return item['title'] + '. ' + item['content']
    
    def getTitle(self, item):
        return item['title']
    
    def getShortDescription(self, item):
        return item['description']
    
    def fetchPage(self, link, item):
        try:
            fp = urllib.request.urlopen(link, timeout = self.timeout)
            mybytes = fp.read()
            page = mybytes.decode("utf8")
            fp.close()
        except socket.timeout as e:
            print(type(e))
            print(link)
            print("There was an error: %r" % e)
            return None  
        except urllib.error.HTTPError as e:
            print(type(e))
            print(link)
            print("There was an error: %r" % e)
            return None
        except urllib.error.URLError as e:
            print(type(e))
            print(link)
            print("There was an error: %r" % e)
            return None 

        self.html = ''
        soup = BeautifulSoup(page, features="html.parser")
        title = soup.find('title');
        description = soup.find("meta", {"name": "description"}).attrs['content']
        date = soup.find('time')
        dateString = date.get('datetime') if date else item['pubDate']
        item = {
            'title': re.sub(' - BBC News$', '', title.text),
            'description': description,
            'pubDate': dateString,
            'link': link,
            'content': self.getPageContent(soup)
        }
        return item
    
    def getPageContent(self, soup):
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
                elif item.name in ['p', 'ul', 'li', 'ol', 'h2', 'h3']:
                    value = str(item.text)
                    text += value + ' '
                    if value:
                        self.html += '<' + item.name + '>' + value + '</' + item.name + '>'
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
                if item.name in ['p', 'ul', 'li', 'ol', 'h2', 'h3']:
                    value = str(item.text)
                    text += value + ' '
                    if value:
                        self.html += '<' + item.name + '>' + value + '</' + item.name + '>'
        return text

    
    