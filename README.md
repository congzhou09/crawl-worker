### Intro

◆ The crawl flow is originated from [OpenAI answer website questions demo](https://github.com/openai/openai-cookbook/tree/main/apps/web-crawl-q-and-a).

◆ Following processes was added or modified to fit practical situations.

1. Wait a few seconds in a random range before crawling a new web page.

2. Use Playwright to fetch more valid HTML content from web pages.

3. Use [Trafilatura](https://github.com/adbar/trafilatura) to gather more valid text from html.

4. Filter URLs with '#' in their name that have duplicate content.

5. Skip some processes when running again.

6. Ramp up robust when there is an exception.

7. Add a logger that records more details.

### Usage

● Python file "run_crawl.py" is the main procedure.
● Use "re_chug.py" to batch crawl failed web pages.