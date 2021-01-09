import json

class Core:

  def __init__(self, format = "json"):
    self.format = format
    return


  def load(self, content):
    if self.format == 'json':
      return json.loads(content)

    return content
  
  def getDate(self, item):
    return item['pubDate']
  
  def getIdentifier(self, item):
    return item['link']

