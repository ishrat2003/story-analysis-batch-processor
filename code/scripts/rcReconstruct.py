import os, sys, logging, json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
packagesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../packages")
sys.path.append(packagesPath)

envPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(dotenv_path=envPath)

from params.rc import RC as Params
from file.core import Core as File
from filesystem.directory import Directory
from loader.bbc import BBC as BBCLoader
from writer.rc import RC as Writer

from rc.context import Context as RCContext

logging.info("# Starting  ")

logging.info("# ================================")

scriptParams = Params()
params = scriptParams.get()
loader = BBCLoader()
storyWriter = Writer(params.destination_directory)
processor = RCContext(loader, storyWriter)
filePath = os.path.join(params.source_directory, params.word_key + '.json')
logging.info('Loading ' + filePath)
processor.process(filePath, params.word_key, params.start_date, params.end_date);

logging.info('Finished')
logging.info("# ================================")