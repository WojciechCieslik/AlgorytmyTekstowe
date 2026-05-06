import scrapy
import json
from pathlib import Path
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import recipe_assets

class MySpider(scrapy.Spider):
    name = 'my_spider'

    start_urls = [
        'https://poprostupycha.com.pl/post-sitemap.xml',
        'https://poprostupycha.com.pl/post-sitemap2.xml'
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 2.0,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'My Bot (szymonstar690@gmail.com)',
        'LOG_LEVEL': 'INFO'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.output_path = recipe_assets.project_main_directory / "json_data" / "pycha_recipes.json"
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, 'w', encoding='utf-8'):
            pass

        print(f"Initialized MySpider - output path: [{str(self.output_path)}]")

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'xml')
        links = [loc.text for loc in soup.find_all('loc') if '/przepis' in loc.text]

        LIMIT_PER_XML = 1000
        links = links[:LIMIT_PER_XML]

        self.logger.info(f'Found {len(links)} recipe links in sitemap.')

        for item_url in links:
            yield scrapy.Request(item_url, self.parse_item)

    def parse_item(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        title = soup.find('h1', class_='entry-title')
        name = title.get_text(strip=True) if title else "unknown"

        ingredients = [
            li.get_text(strip=True)
            for li in soup.find_all('li', itemprop='recipeIngredient')
        ]

        if ingredients:
            recipe = {
                "url": response.url,
                "recipe_name": name,
                "ingredients": ingredients
            }

            self.logger.info(f"Saving recipe: {name}")

            with open(self.output_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(recipe, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MySpider)
    process.start()