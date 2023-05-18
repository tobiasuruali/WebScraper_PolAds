import scrapy
from scrapy.crawler import CrawlerProcess
import json
import csv
import pandas as pd
from urllib.parse import urlparse, parse_qs
import time

class CSVWriter:
    def __init__(self, filename):
        self.file = open(filename, 'a', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=['ad_id','ad_url', 'youtube_url'])
        self.writer.writeheader()
    
    def write_row(self, cr_value, ad_url, youtube_url):
        self.writer.writerow({'ad_id': cr_value,'ad_url': ad_url, 'youtube_url': youtube_url})
    
    def close(self):
        self.file.close()


class AdspiderSpider(scrapy.Spider):
    name = "adspider"
    allowed_domains = ["adstransparency.google.com"]
    
    # Read the start_urls from the us_video_rows.fst file
    df = pd.read_parquet('data/data_processed/us_video_ads_sample.parquet')
    # Initialize the 'youtube_url' column in the DataFrame
    df['youtube_url'] = ''
    start_urls = df['ad_url'].tolist()
    
    # Set batch size to 8
    batch_size = 8
    
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_writer = CSVWriter('results.csv')
    
    def start_requests(self):
        for i in range(0, len(self.start_urls), self.batch_size):
            batch_urls = self.start_urls[i:i+self.batch_size]
            for url in batch_urls:
                # Parse the URL to extract the AR* and CR* values
                parsed_url = urlparse(url)
                path_parts = parsed_url.path.split('/')
                ar_value = path_parts[2]
                cr_value = path_parts[4]

                # Generate the body of the POST request
                body = f'f.req=%7B%221%22%3A%22{ar_value}%22%2C%222%22%3A%22{cr_value}%22%2C%225%22%3A%7B%221%22%3A2%7D%7D'

                yield scrapy.Request(
                    url="https://adstransparency.google.com/anji/_/rpc/LookupService/GetCreativeById?authuser=",
                    callback=self.parse,
                    method='POST',
                    headers=self.headers,
                    body=body,
                    cb_kwargs=dict(batch_index=i, url_index=self.start_urls.index(url), cr_value=cr_value, url=url)
                )
            # Pause for 10 seconds before processing the next batch of start_urls
            time.sleep(10)

    def parse(self, response, batch_index, url_index, cr_value, url):
        data = json.loads(response.text)
        # print(data)

        try:
            # Extract the YouTube link from the JSON data
            youtube_link = data['1']['5'][0]['2']['4']
            # Write the cr_value and youtube_url to the CSV file
            self.csv_writer.write_row(cr_value=cr_value, ad_url=url, youtube_url=youtube_link)
            print(f'Successfully extracted YouTube link for URL index {url_index} : {youtube_link}')
        except:
            # If there is an error, write 'NoVideo' to the CSV file
            self.csv_writer.write_row(cr_value=cr_value, ad_url=url, youtube_url='NoVideo')
            print(f'Failed to extract YouTube link for URL index {url_index}')
    
    def closed(self, reason):
        self.csv_writer.close()

# Run the spider using CrawlerProcess
process = CrawlerProcess()
process.crawl(AdspiderSpider)
process.start()
