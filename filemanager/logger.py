import logging

class Logger:
  @staticmethod
  def setup_logging(debug):
      level = logging.DEBUG if debug else logging.INFO
      logging.basicConfig(
          level=level,
          format='%(asctime)s - %(levelname)s - %(message)s',
      )

