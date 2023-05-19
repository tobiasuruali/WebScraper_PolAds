import scrapy
from scrapy.crawler import CrawlerProcess
import json
import pandas as pd
from urllib.parse import urlparse, parse_qs
import time
import sys
from pathlib import Path
import os
import pickle

# Get the absolute path to the parent directory of this script
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to the Python path
sys.path.append(str(parent_dir))

from items import AdItem


class AdSpider(scrapy.Spider):
    name = "adspider"
    allowed_domains = ["adstransparency.google.com"]

    # Set the folder containing the parquet files
    folder = "../data/data_processed/us_video_ads_batch"

    # Load the processed_files set from a file if it exists
    try:
        with open("processed_files.pkl", "rb") as f:
            processed_files = pickle.load(f)
            print(f"Loaded processed_files set from file: {processed_files}")
    except FileNotFoundError:
        processed_files = set()
        print("Setting processed_files: .... Set to empty Set")

    # Set batch size to 32
    batch_size = 32

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Framework-Xsrf-Token": "",
        "X-Same-Domain": "1",
    }

    def start_requests(self):
        print("Starting requests.........")

        for filename in os.listdir(self.folder):
            if filename.endswith(".parquet") and filename not in self.processed_files:
                print(f"Processing file: {filename}")

                filepath = os.path.join(self.folder, filename)
                df = pd.read_parquet(filepath)
                start_urls = df["ad_url"].tolist()

                for i in range(0, len(start_urls), self.batch_size):
                    batch_urls = start_urls[i : i + self.batch_size]
                    for url in batch_urls:
                        # Parse the URL to extract the AR* and CR* values
                        parsed_url = urlparse(url)
                        path_parts = parsed_url.path.split("/")
                        ar_value = path_parts[2]
                        cr_value = path_parts[4]

                        # Generate the body of the POST request
                        body = f"f.req=%7B%221%22%3A%22{ar_value}%22%2C%222%22%3A%22{cr_value}%22%2C%225%22%3A%7B%221%22%3A2%7D%7D"

                        yield scrapy.Request(
                            url="https://adstransparency.google.com/anji/_/rpc/LookupService/GetCreativeById?authuser=",
                            callback=self.parse,
                            method="POST",
                            headers=self.headers,
                            body=body,
                            cb_kwargs=dict(
                                batch_index=i,
                                url_index=start_urls.index(url),
                                cr_value=cr_value,
                                url=url,
                            ),
                        )
                    # Pause for 10 seconds before processing the next batch of start_urls
                    time.sleep(10)

                self.processed_files.add(filename)

                # Save the processed_files set to a file after processing each parquet file
                with open("processed_files.pkl", "wb") as f:
                    pickle.dump(self.processed_files, f)

                # Stop after processing one parquet file
                break

    def parse(self, response, batch_index, url_index, cr_value, url):
        data = json.loads(response.text)

        aditem = AdItem()
        aditem["ad_id"] = cr_value
        aditem["ad_url"] = url

        try:
            # Extract the YouTube link from the JSON data
            youtube_link = data["1"]["5"][0]["2"]["4"]
            aditem["youtube_url"] = youtube_link
            print(
                f"Successfully extracted YouTube link for URL index {url_index} : {youtube_link}"
            )
        except:
            # If there is an error, set 'youtube_url' to 'NoVideo'
            aditem["youtube_url"] = "NoVideo"
            print(f"Failed to extract YouTube link for URL index {url_index}")

        yield aditem

    def close(self, reason):
        start_time = self.crawler.stats.get_value("start_time")
        finish_time = self.crawler.stats.get_value("finish_time")
        print("Total run time: ", finish_time - start_time)


# Run the spider using CrawlerProcess
# Commented out when scrapy crawl adspider was used
# process = CrawlerProcess()
# process.crawl(AdSpider)
# process.start()