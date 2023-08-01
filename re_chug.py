from common.logger.logger import logger
from crawl import crawl

rechug_urls = [
    'https://www.langchain.asia/modules/indexes/retrievers/examples/contextual-compression',
    'https://www.langchain.asia/modules/indexes/retrievers/examples/contextual-compression#contextual-compression-retriever',
    'https://www.langchain.asia/modules/indexes/retrievers/examples/contextual-compression#stringing-compressors-and-document-transformers-together',
]

for one_url in rechug_urls:
    crawl(one_url, wait_sec=5)

logger.info("done")
