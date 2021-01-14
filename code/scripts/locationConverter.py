import os, sys, logging, json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
packagesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../packages")
sys.path.append(packagesPath)

envPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(dotenv_path=envPath)

locationPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../story-analysis-data")

from file.tsv import Tsv
from file.json import Json

tsvFileProcess = Tsv()
jsonFileProcessor = Json() 
   
data = tsvFileProcess.read(locationPath + '/map/world_population.tsv');
countries = []
names = []

for index, item in data.iterrows():
    countries.append({
        'id': item['id'],
        'name': item['name']
    })
    names.append(item['name'])


jsonFileProcessor.write(locationPath + '/gc/countries.json', countries);
jsonFileProcessor.write(locationPath + '/gc/countryNames.json', names);
print('Finished')