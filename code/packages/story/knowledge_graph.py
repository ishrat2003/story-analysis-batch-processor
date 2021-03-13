from __future__ import print_function
import json
import urllib
import os
import http, socket
from .category import Category

class KnowledgeGraph():
    
    def __init__(self, categorySourcePath):
        self.endPoint = 'https://kgsearch.googleapis.com/v1/entities:search'
        self.apiKey = os.environ['GOOGLE_KNOWLEDGE_GRAPH']
        self.category = Category(categorySourcePath)
        self.timeout = int(os.environ['TIMEOUT'])
        self.reset()
        return
    
    def reset(self):
        self.objects = {}
        self.categories = {}
        self.links = []
        self.nodeKeys = []
        return
    
    def getObjects(self):
        return self.objects
    
    def getObjectDetails(self, key):
        if key not in self.objects.keys():
            return None
        return self.objects[key]
    
    def getCategories(self):
        return self.categories
    
    def getGraph(self, words, storyKeys):
        graphNodes = []
        graphLinks = []
        if not len(storyKeys) or not len(words):
            return {
                "nodes": graphNodes,
                "links": graphLinks
            }
            
        storyNodeKeys = []
        for link in self.links:
            if (link["type"] in storyKeys) and (link["source"] in storyKeys) and (link["target"] in storyKeys):
                if link["source"] not in storyNodeKeys:
                    storyNodeKeys.append(link["source"])
                if link["target"] not in storyNodeKeys:
                    storyNodeKeys.append(link["target"]) 
                graphLinks.append({
                    "source": storyNodeKeys.index(link["source"]),
                    "target": storyNodeKeys.index(link["target"]),
                    "type": words[link["type"]]["pure_word"]
                })
                
        for key in storyNodeKeys:
            node = {
                "name": words[key]['pure_word'],
                "tooltip": "",
                "label": "",
                "color": "default",
                "id": storyNodeKeys.index(key)
            }
            if key in self.objects.keys():
                node["tooltip"] = self.objects[key]["tooltip"]
                node["label"] = self.objects[key]["label"]
                node["color"] = self.objects[key]["label"].lower()
                
            graphNodes.append(node)
        
        return {
                "nodes": graphNodes,
                "links": graphLinks
            }
        
        
    def addLink(self, sentence):
        objects = []
        verbs = []
        for word in sentence:
            if (len(objects) >= 1) and (word['type'][0] == 'V'):
                verbs.append(word)
            else:
                objects.append(word['stemmed_word'])

            if (len(objects) >= 2) and (len(verbs) >= 1):
                length = len(objects)
                node1Key = objects[length - 2]
                node2Key = objects[length - 1]
                objects = [node2Key]
                for verb in verbs:
                    link = {
                        "source": node1Key,
                        "target": node2Key,
                        "type": verb['stemmed_word']
                    }
                    
                    # print(node1Key, '--', node2Key, '--',verb['stemmed_word'])
                    self.links.append(link)
                    
                if node1Key not in self.nodeKeys:
                    self.nodeKeys.append(node1Key)
                if node2Key not in self.nodeKeys:
                    self.nodeKeys.append(node2Key)
                
                
        return
        
    
    def addObject(self, key, query):
        params = {
            'query': query,
            'limit': 1,
            'indent': True,
            'key': self.apiKey,
        }

        url = self.endPoint + '?' + urllib.parse.urlencode(params)
        response = json.loads(urllib.request.urlopen(url).read())
        
        if not response or ('itemListElement' not in response.keys()) or not response['itemListElement'] or not response['itemListElement'][0]['result']:
            if self.isPerson(query.lower()):
                self.objects[key] = {
                    "name": query,
                    "tooltip": "Individual",
                    "label": "Person",
                }
                self.appendCategoryItem("Person", query)
                return True
            return False
        
        if response['itemListElement'][0]['resultScore'] < 5:
            return False
        
        category = self.category.get(query)
        if not category:
            category = self.getCategory(response['itemListElement'][0]['result'])
        self.objects[key] = {
            "name": query,
            "tooltip": self.getDescription(response['itemListElement'][0]['result']),
            "label": category
        }
        self.appendCategoryItem(category, query)
        
        return True
    
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
        except urllib.error.HTTPError as e:
            print(type(e))
            print(url)
            print("There was an error: %r" % e)
            return None
        except urllib.error.URLError as e:
            print(type(e))
            print(url)
            print("There was an error: %r" % e)
            return None
        except  http.client.HTTPException as e:
            print(type(e))
            print(url)
            print("There was an error: %r" % e)
            return None

        response = json.loads(response)
        
        if not response or ('itemListElement' not in response.keys()) or not response['itemListElement'] or not response['itemListElement'][0]['result']:
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
