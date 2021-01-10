from __future__ import print_function
import json
import urllib
import socket
import os

class KnowledgeGraph():
    
    def __init__(self):
        self.endPoint = 'https://kgsearch.googleapis.com/v1/entities:search'
        self.apiKey = os.environ['GOOGLE_KNOWLEDGE_GRAPH']
        self.timeout = int(os.environ['TIMEOUT'])
        self.reset()
        return
    
    def reset(self):
        self.categories = {}
        return
    
    def getMoreDetails(self, key, query):
        params = {
            'query': query,
            'limit': 1,
            'indent': True,
            'key': self.apiKey,
        }
        url = self.endPoint + '?' + urllib.parse.urlencode(params)
        
        try:
            response = urllib.request.urlopen(url, timeout = self.timeout).read()
        except socket.timeout as e:
            print(type(e))
            print(url)
            print("There was an error: %r" % e)
            return None

        response = json.loads(response)
        
        if not response or ('itemListElement' not in response.keys()) or not response['itemListElement'] or not response['itemListElement'][0]['result']:
            if self.isPerson(query.lower()):
                self.appendCategoryItem("Person", query)
                return {
                    "description": "Individual",
                    "category": "Person",
                }
            return None
        
        if response['itemListElement'][0]['resultScore'] < 5:
            return False
        
        category = self.getCategory(response['itemListElement'][0]['result'])
        self.appendCategoryItem(category, query)
        return {
            "description": self.getDescription(response['itemListElement'][0]['result']),
            "category": category
        }
    
    def appendCategoryItem(self, category, item):
        if category not in self.categories.keys():
            self.categories[category] = []
            
        if item not in self.categories[category]:
            self.categories[category].append(item);
        return
    
    def getDescription(self, item):
        if not item:
            return ''
        
        if 'detailedDescription' not in item.keys():
            return ''
        
        if 'articleBody' in item['detailedDescription'].keys():
            return item['detailedDescription']['articleBody']
        
        return ''
    
    def getCategory(self, result):
        if '@type' not in result.keys():
            # print('--------')
            # print(result)
            return ''
        
        types = result['@type']
        if 'Person' in types:
            return 'Person'
        
        if ('Place' in types) or ('Country' in types) or ('City' in types):
            return 'Location'
        
        if self.isTime(result):
            return 'Time'
        
        if ('Organization' in types) or ('EducationalOrganization' in types):
            return 'Organization'
        
        types.remove('Thing')
        if types:
            return types[0]
        
        return 'Others'
    
    def isTime(self, item):
        if ('description' in item.keys()) and (item["description"] in ['Day of week', 'Month']):
            return True
        if ('detailedDescription' in item.keys()) and ('articleBody' in item['detailedDescription'].keys()) and self.stringContains(item['detailedDescription']['articleBody'].lower(), 'festival'):
            return True
        return False
            
    
    def isPerson(self, text):
        for title in ['mr', 'mrs', 'miss', 'dr', 'doctor', 'prof', 'professor']:
            if self.stringContains(text, title + ' '):
                return True
            
        return False
    
    def stringContains(self, text, subText):
        if not text or (text.find(subText) == -1):
            return False
        return True
