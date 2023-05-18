import scrapy
import json
import csv
import pandas as pd
from urllib.parse import urlparse, parse_qs

class AdspiderSpider(scrapy.Spider):
    name = "adspider"
    allowed_domains = ["adstransparency.google.com"]
    
    # Read the start_urls from the us_video_rows.fst file
    df = pd.read_parquet('data/data_processed/us_video_ads_sample.parquet')
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
                    cb_kwargs=dict(batch_index=i, url_index=self.start_urls.index(url))
                )
    
    def parse(self, response, batch_index, url_index):
        data = json.loads(response.text)
        
        try:
            # Extract the YouTube link from the JSON data
            youtube_link = data['1']['5'][0]['2']['4']
            # Add the youtube_link to the corresponding row in the original DataFrame
            self.df.loc[url_index, 'youtube_url'] = youtube_link
        except:
            # If there is an error, write 'NoVideo' in the DataFrame
            self.df.loc[url_index, 'youtube_url'] = 'NoVideo'
        
         # Check if all rows in the current batch have been processed
        if (url_index + 1) % self.batch_size == 0 or url_index == len(self.start_urls) - 1:
            # Write only the processed rows in the current batch to a CSV file
            start_index = batch_index * self.batch_size
            end_index = start_index + self.batch_size
            self.df.iloc[start_index:end_index].to_csv('processed_urls.csv', mode='a', header=False, index=False)
    