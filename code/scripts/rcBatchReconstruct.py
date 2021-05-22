import os, sys, logging, json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
packagesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../packages")
sys.path.append(packagesPath)

envPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(dotenv_path=envPath)

from params.core import Core as Params
from rc.batch import Batch


logging.info("# Starting  ")

logging.info("# ================================")

scriptParams = Params()
params = scriptParams.get()
scriptPath = os.path.abspath(os.getcwd())
logging.info('Source ' + params.source_directory)
logging.info('Destination ' + params.destination_directory)
batchProcessor = Batch(params.source_directory, params.destination_directory, scriptPath)
batchProcessor.process()
logging.info('Finished')
logging.info("# ================================")