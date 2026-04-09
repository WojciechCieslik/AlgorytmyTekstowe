import scrapy
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess

class MySpider(scrapy.Spider):
    name = 'my_spider'

    start_urls = [
        'https://poprostupycha.com.pl/post-sitemap.xml',
        'https://poprostupycha.com.pl/post-sitemap2.xml'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': '2.0',
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'My Bot (szymonstar690@gmail.com)',
        'LOG_LEVEL': 'INFO'
    }

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'xml')
        links = [loc.text for loc in soup.find_all('loc') if '/przepis' in loc.text]

        LIMIT_PER_XML = 1000;

        if len(links) > LIMIT_PER_XML:
            links = links[:LIMIT_PER_XML]

        self.logger.info(f'Found {len(links)} recipe links in sitemap.')

        for item_url in links:
            yield scrapy.Request(item_url, self.parse_item)
        
    def parse_item(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        
        name = response.url.strip('/').split('/')[-1]
        name = name.replace('-', ' ')

        title = soup.find('h1', class_='entry-title')
        name = title.get_text(strip=True)
        ingredients = [li.get_text(strip=True) for li in soup.find_all('li', itemprop='recipeIngredient')]

        if ingredients:
            self.logger.info(f'Adding recipe for: {{ {name} }}')

            yield {
                'url': response.url,
                'name': name,
                'ingredients': ingredients
            }

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MySpider)
    process.start()
