import argparse
import os
import logging
import json

class Core:

  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('--source_directory')
    self.parser.add_argument('--destination_directory')
    self.parser.add_argument('--total_items', default=0, help = "Total items of data for processing")
    return

  def get(self):
    return self.parser.parse_args()
