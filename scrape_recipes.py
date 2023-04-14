import scrapy
from scrapy.crawler import CrawlerProcess

class RecipeSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.valdemarsro.dk/nem-hverdagsmad/']

    def parse(self, response):
        for post in response.css('.post-list-item'):
            if "banner" not in post.get():
                yield {'post':post.css("a").attrib["href"]}

        for nav in response.css(".pagenav-new"):
            for link in nav.css("a"):
                yield response.follow(link, self.parse)

process = CrawlerProcess(settings={
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)', 
    'FEEDS': {
        'recipes.csv': {'format': 'csv', 'overwrite': True}
    }
})
process.crawl(RecipeSpider)
process.start()

items = {v["href"] for p in range(1, 11) for v in scrape_me("https://www.valdemarsro.dk/familiefavoritter/page/{p}").links() if v.get("href", "").startswith("https://www.valdemarsro.dk/")}
