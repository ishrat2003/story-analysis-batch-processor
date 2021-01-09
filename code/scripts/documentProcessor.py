import os, sys, logging, json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
packagesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../packages")
sys.path.append(packagesPath)

envPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(dotenv_path=envPath)

from params.core import Core as Params
from file.core import Core as File
from filesystem.directory import Directory
from loader.bbc import BBC as BBCLoader
from writer.core import Core as Writer

from lc.context import Context as LCContext

logging.info("# Starting  ")

logging.info("# ================================")

scriptParams = Params()
params = scriptParams.get()
loader = BBCLoader()
storyWriter = Writer(params.destination_directory)
processor = LCContext(loader, storyWriter)

sourceDirectory = Directory(params.source_directory)
sourceDirectory.process(processor, params.total_items)

print('Finished')