import scrapy
# from scrapy_splash import SplashRequest

class TestAdspiderSpider(scrapy.Spider):
    name = "adspider"
    allowed_domains = ["adstransparency.google.com"]
    start_urls = ["https://adstransparency.google.com/advertiser/AR06503673263263055873/creative/CR05870336561161175041?region=US"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                args={'wait': 0.5},
            )

    def parse(self, response):
        # Use a CSS selector to extract the embedded YouTube link
        youtube_link = response.css('iframe[src*="youtube.com"]::attr(src)').get()
        # Do something with the extracted link
        print("Extracted link: ", youtube_link)

# Create a CrawlerProcess with some settings
process = CrawlerProcess(settings={
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

# Add the spider to the process and start the crawling process
process.crawl(AdspiderSpider)
process.start()