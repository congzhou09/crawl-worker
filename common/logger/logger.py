import os
from common.util.logging import get_logger

current_path = os.path.dirname(__file__)
config_path = os.path.join(current_path, './', 'log-config.json').strip()

logger=get_logger(config_path, "one-client")

