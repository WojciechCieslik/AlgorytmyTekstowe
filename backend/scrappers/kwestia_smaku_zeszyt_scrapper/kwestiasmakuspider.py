import scrapy
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
import json
import re
from datetime import datetime

def split_ingredient(text):
    """
    Próbuje rozdzielić tekst składnika na (nazwa, ilość).
    Obsługuje formaty: '200 g mąki', '1 szklanka cukru', 'szczypta soli'.
    """
    text = text.strip()
    if not text:
        return '', ''

    pattern = r'^([\d\.,]+\s*[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\.]*)'
    match = re.match(pattern, text)
    
    if match:
        quantity = match.group(1).strip()
        name = text[match.end():].strip()
        if not name:
            name = quantity
            quantity = ''
        return name, quantity
    else:
        return text, ''

class KwestiaSmakuSpider(scrapy.Spider):
    name = 'kwestiasmaku'

    start_urls = [
        'https://www.kwestiasmaku.com/przepisy',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2.0,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'My Bot (saurfang321@gmail.com)',
        'LOG_LEVEL': 'INFO'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/przepis/' in href:
                links.append(response.urljoin(href))
        
        LIMIT_PER_PAGE = 500
        if len(links) > LIMIT_PER_PAGE:
            links = links[:LIMIT_PER_PAGE]
        
        self.logger.info(f'Found {len(links)} recipe links on {response.url}')
        
        for item_url in links:
            yield scrapy.Request(item_url, self.parse_item)
        
        next_page = soup.find('a', class_='pager__item--next') or \
                    soup.find('a', title='Przejdź do następnej strony') or \
                    soup.find('a', string='›')
        if next_page and next_page.get('href'):
            yield response.follow(next_page['href'], self.parse)

    def parse_item(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        
        title_tag = soup.find('h1', class_='page-header') or soup.find('h1')
        name = title_tag.get_text(strip=True) if title_tag else ''
        
        raw_ingredients = []
        ing_container = (
            soup.find('div', class_='field-name-field-skladniki') or
            soup.find('div', class_='field--name-field-skladniki') or
            soup.find('ul', class_='ingredients')
        )
        if ing_container:
            raw_ingredients = [li.get_text(strip=True) for li in ing_container.find_all('li')]
        else:
            script = soup.find('script', type='application/ld+json')
            if script:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Recipe':
                                raw_ingredients = item.get('recipeIngredient', [])
                                break
                    elif data.get('@type') == 'Recipe':
                        raw_ingredients = data.get('recipeIngredient', [])
                except:
                    pass
        
        ingredients = []
        for ing_text in raw_ingredients:
            ing_text = ing_text.strip()
            if ing_text:
                ingredients.append(ing_text)
        
        if name and ingredients:
            self.logger.info(f'Adding recipe: {name}')
            item = {
                'url': response.url,
                'recipe_name': name,
                'ingredients': ingredients
            }
            self.results.append(item)
            yield item

    def closed(self, reason):
        if self.results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'kwestiasmaku_{timestamp}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            self.logger.info(f'Zapisano {len(self.results)} przepisów do pliku {filename}')
        else:
            self.logger.warning('Brak zebranych przepisów – plik nie został utworzony.')

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(KwestiaSmakuSpider)
    process.start()
