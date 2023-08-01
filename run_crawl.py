from common.logger.logger import logger
from crawl import crawl


# full_url = "https://openai.com"
full_url = "https://python.langchain.com/docs/get_started"
# full_url = (
#     "https://www.langchain.asia/modules/indexes/document_loaders/examples/web_base"
# )

crawl(full_url, wait_sec=5)
logger.info("done")
