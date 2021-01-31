import os, sys, logging, json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
packagesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../packages")
sys.path.append(packagesPath)

envPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(dotenv_path=envPath)

locationPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../story-analysis-data")

from file.json import Json
from cluster.hierarchy import Hierarchy

jsonFileProcessor = Json() 
hierarchyProcessor = Hierarchy()

data = jsonFileProcessor.read(locationPath + '/words/vaccin.json');
tree = hierarchyProcessor.getTree(data)
print(tree)


# jsonFileProcessor.write(locationPath + '/hierarchy/vaccin.json', tree);
print('Finished')