import scrapy
from scrapy.spiders import SitemapSpider

class PrzepisySpider(scrapy.Spider):
    name = 'przepisy_spider'

    # Zamiast mapy strony, podaje główne kategorie
    start_urls = [
        # 'https://www.przepisy.pl/przepisy/dania-i-przekaski',
        # 'https://www.przepisy.pl/przepisy/na-skroty',
        'https://www.przepisy.pl/przepisy/kuchnie-swiata',
        'https://www.przepisy.pl/przepisy/kuchnie-swiata/kuchnia-polska',
        'https://www.przepisy.pl/przepisy/dania-i-przekaski/dania-glowne',
        'https://www.przepisy.pl/przepisy/dania-i-przekaski/jednogarnkowe',
        'https://www.przepisy.pl/przepisy/dania-i-przekaski/dania-maczne',
        'https://www.przepisy.pl/przepisy/dania-i-przekaski/makarony',
        'https://www.przepisy.pl/przepisy/dania-i-przekaski/street-food',
        'https://www.przepisy.pl/przepisy/dania-i-przekaski/zapiekanki',
        'https://www.przepisy.pl/przepisy/dania-i-przekaski/pizze',
        'https://www.przepisy.pl/przepisy/dania-i-przekaski/zupy',
        # 'https://www.przepisy.pl/przepisy/na-skroty/przepisy-z-5-skladnikow',
        # 'https://www.przepisy.pl/przepisy/na-skroty/przepisy-z-4-skladnikow',
        # 'https://www.przepisy.pl/przepisy/na-skroty/przepisy-z-3-skladnikow',
        # 'https://www.przepisy.pl/przepisy/na-skroty/szybkie-przepisy/szybkie-dania',
        # 'https://www.przepisy.pl/przepisy/obiad/szybki-obiad'
    ]

    custom_settings = {
        # 'CLOSESPIDER_PAGECOUNT': 1100,
        'CLOSESPIDER_ITEMCOUNT': 2000,
        # 'DEPTH_STATS_VERBOSE': True,
        'DEPTH_LIMIT': 0,
        'DOWNLOAD_DELAY': 3.0,
        'ROBOTSTXT_OBEY': False,
        'AUTOTHROTTLE_ENABLED': True,
        'USER_AGENT': "Mozilla/5.0",
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse(self, response):
        """Główna funkcja parsująca listy przepisów (kategorie i paginację)"""

        # 1. Wyciągamy linki do przepisów
        recipe_links = response.css('a[href*="/przepis/"]::attr(href)').getall()
        self.logger.info(f"Znaleziono {len(recipe_links)} przepisów na stronie: {response.url}")

        for link in recipe_links:
            # FILTRACJA: Jeśli link zawiera frazę 'przepisy-uzytkownikow', jest pomijany
            if 'przepisy-uzytkownikow' in link:
                continue
            yield response.follow(link, callback=self.parse_recipe)

        # 2. Paginacja
        # Szuka strzałki w prawo, która NIE ma klasy 'pagination__btn--disabled'
        next_page = response.css('a.pagination__btn--arrow--right:not(.pagination__btn--disabled)::attr(href)').get()

        if next_page:
            self.logger.info(f"PRZECHODZĘ DO NASTĘPNEJ STRONY: {next_page}")
            # Rekurencyjnie wywołuje 'parse' dla kolejnej strony (?page=2, 3...)
            yield response.follow(next_page, callback=self.parse)

    def parse_recipe(self, response):
        """Parsuje konkretny przepis"""
        title = response.css('h1::text').get() or response.css('h1.display-1::text').get()
        title = title.strip() if title else "Brak tytułu"

        ingredients_list = []
        items = response.css('div.ingredients-list-content-item')

        for item in items:
            name = item.css('.ingredient-name .text-bg-white::text').get()
            quantity = item.css('.quantity .text-bg-white::text').get()

            clean_name = name.strip() if name else None
            clean_quantity = quantity.strip() if quantity else ""

            if clean_name:
                ingredients_list.append(clean_name+" "+clean_quantity)

        if ingredients_list:
            yield {
                'url': response.url,
                'recipe_name': title,
                'ingredients': ingredients_list,
            }