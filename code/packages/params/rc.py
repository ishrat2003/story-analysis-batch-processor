from .core import Core

class RC(Core):

  def __init__(self):
    super().__init__()
    self.parser.add_argument('--start_date')
    self.parser.add_argument('--end_date')
    self.parser.add_argument('--word_key')
    return
