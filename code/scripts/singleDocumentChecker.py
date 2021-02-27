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

processor.process(json.dumps({
    "title": "Captain Sir Tom Moore's funeral to be 'spectacular'",
    "description": "A small, family service will begin soon for the 100-year-old who raised almost £33m for the NHS.",
    "link": "https://www.bbc.co.uk/news/uk-england-beds-bucks-herts-56212135",
    "pubDate": "Sun, 27 Feb 2021 00:06:18 GMT"
}));

logging.info('Finished')
logging.info("# ================================")