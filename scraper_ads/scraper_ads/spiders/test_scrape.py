import scrapy
import json
import csv
from urllib.parse import urlparse, parse_qs

class AdspiderSpider(scrapy.Spider):
    name = "adspider"
    allowed_domains = ["adstransparency.google.com"]
    start_urls = [
        "https://adstransparency.google.com/advertiser/AR06503673263263055873/creative/CR05870336561161175041?region=US",
        "https://adstransparency.google.com/advertiser/AR17896267392510590977/creative/CR18102955856042655745?region=US",
        "https://adstransparency.google.com/advertiser/AR11825178974693097473/creative/CR03980852629424046081?region=US&",
        "https://adstransparency.google.com/advertiser/AR02263241812720222209/creative/CR16714562941231300609?region=US"
    ]

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Framework-Xsrf-Token": "",
        "X-Same-Domain": "1",
    }

    def start_requests(self):
        for url in self.start_urls:
            # Parse the URL to extract the AR* and CR* values
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('/')
            ar_value = path_parts[2]
            cr_value = path_parts[4]
            print(f'parsed_url: {parsed_url}')
            print(f'path_parts: {path_parts}')           
            
            print("AdvertiserID: ",ar_value," & CreativeID: ", cr_value)
            # Generate the body of the POST request
            body = f'f.req=%7B%221%22%3A%22{ar_value}%22%2C%222%22%3A%22{cr_value}%22%2C%225%22%3A%7B%221%22%3A2%7D%7D'

            yield scrapy.Request(
                url="https://adstransparency.google.com/anji/_/rpc/LookupService/GetCreativeById?authuser=",
                callback=self.parse,
                method='POST',
                headers=self.headers,
                body=body
            )

    def parse(self, response):
        data = json.loads(response.text)
        # Extract the YouTube link from the JSON data
        youtube_link = data['1']['5'][0]['2']['4']
        # Do something with the extracted link
        with open('youtube_links.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([youtube_link])
