# Political Ad Webscraping Sentiment Analysis

This project analyzes a dataset containing all political ads that have run on Google platforms in the United States since May 2018. The goal is to explore the sentiment difference between Trump and Biden advertisements using GPT-3.5 Turbo as our sentiment analyzer.

## Instructions

To run this project, follow these steps:

1. Set up Docker by following the instructions [here](https://docs.docker.com/get-docker/).
2. Run the Rselenium docker image with this command:  
 ```bash
 docker run -d -p 4445:4444 -p 5901:5900 --shm-size="2g" selenium/standalone-firefox:4.8.3-20230403
 ```    
 This command runs a Docker container with the `selenium/standalone-firefox:4.8.3-20230403` image in detached mode. Port 4444 in the container (the Selenium port) is mapped to port 4445 on the host machine. Port 5900 in the container is mapped to port 5901 on the host machine, allowing remote access with a VNC viewer. The shared memory size for the container is set to 2GB.

3. Run the scripts in the following order:
    - `01_prepare_dataset_4_url_scrape.R`: This script prepares the dataset for URL scraping.
    - `02_scrape_automation_video_links.R`: This script uses RSelenium to scrape the youtube URLs from a dynamic website.
    - `03_trump_biden_subset.R`: This script selects ads from advertisers that have either "Trump" or "Biden" in their name and randomly selects 25 ads from each group.
    - `04_download_and_transcribe.ipynb`: This script uses Google Colab and the package yt-dlp to download just the audio of each youtube video and transcribes it using OpenAI's Whisper Transcription model.
    - `05_gpt_sentiment_analysis.ipynb`: This script uses GPT-3.5 Turbo to perform sentiment analysis on the transcribed text.

4. For scripts `04_download_and_transcribe.ipynb` and `05_gpt_sentiment_analysis.ipynb`, you will need to create a Google Drive folder called `Google_Pol_Ads`. After that, the folder structure should be the same as this project, with `data/data_processed` and `data/data_raw` folders.


# Scrapy

How to run scrapy spider:
```bash
cd scraper_ads
scrapy crawl adspider
```




## Scrapy Notes

Setting up Delays for ethical scraping:
https://scrapeops.io/python-scrapy-playbook/scrapy-delay-between-requests/


Refer to the [settings.py](scraper_ads/scraper_ads/settings.py) file for more information on the settings.


## Scraped Link Examples

Since the Selenium webscraping is quite slow, I looked for alternative ways to get the youtube links.

*Tutorial:* https://www.youtube.com/watch?v=Pu3gmdWsLYc

I found that the links are stored in a response JSON that is viewable in the developer tools of the browser.

Inside the developer tools, go to Network -> FETCH/XHR -> GetCreativeById?authuser= -> Response
And at the 5th level of the JSON, there is a link to the youtube video.  

https://adstransparency.google.com/anji/_/rpc/LookupService/GetCreativeById?authuser=


### Example Request:
```js
fetch("https://adstransparency.google.com/anji/_/rpc/LookupService/GetCreativeById?authuser=", {
  "headers": {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Google Chrome\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-framework-xsrf-token": "",
    "x-same-domain": "1",
    "cookie": "AEC=AUEFqZdWoJ_T4LaHYoZnqMLmkyKnnTmP0WRIksOZpEWzxcxLnahiQ_O3-f0; CONSENT=PENDING+570; SOCS=CAESHAgCEhJnd3NfMjAyMzA1MTEtMF9SQzQaAmRlIAEaBgiAj4ujBg; NID=511=Vz8SXIE0RLEW6T7OGvqTq0GuMUk-9FNcMIOndKzJa9O70ypL8d_oymDCZNtbCdlqwJ5sFGeDIVcjc13vzE2QwA-krkOT4oTDeUlbpda4ZfaGmMl5OZoqz0R6XzwwuD9bOQlkSekTHcnKF40arq_xYAGLjcQbu5VWT_FRcpXVzDw; __Secure-ENID=12.SE=JJ5rxQVXp6wpP-HgOQy7VKKxNkQXa4oHcCtgPbfsFHImL9qBGaH3qi7HVs-_fLP2-horqlxjFW1xiAaTmv5dvIk6y0XyiDDQnurU0zah_nz3GJgrfvt2fAJAitAjTJlE88VQBOlfCEm2-OU2xyOv_KVtfJzODeGHzNT_Z9FmNAA",
    "Referer": "https://adstransparency.google.com/advertiser/AR06503673263263055873/creative/CR05870336561161175041?region=US&topic=political",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  },
  "body": "f.req=%7B%221%22%3A%22AR06503673263263055873%22%2C%222%22%3A%22CR05870336561161175041%22%2C%225%22%3A%7B%221%22%3A2%7D%7D",
  "method": "POST"
});
```


As you can now see, the Response JSON entails the Youtube link of the embedded video:
### Response:

 ```json

{
    "1": {
        "1": "AR06503673263263055873",
        "2": "CR05870336561161175041",
        "3": {
            "1": "1601176602",
            "2": 897143000
        },
        "4": {
            "1": "1601531970",
            "2": 801951000
        },
        "5": [
            {
                "2": {
                    "4": "https://www.youtube.com/embed/58wGr2umMx4"
                }
            }
        ],
        "6": 5,
        "7": [
            "US"
        ],
        "8": 3,
        "9": "250000",
        "10": "300000",
        "11": {
            "1": [
                {
                    "1": "USD",
                    "2": "4000"
                }
            ]
        },
        "12": {
            "1": [
                {
                    "1": "USD",
                    "2": "4500"
                }
            ]
        },
        "13": {
            "1": {
                "1": [
                    {
                        "1": 7
                    },
                    {
                        "1": 8
                    },
                    {
                        "1": 6
                    }
                ],
                "2": [
                    {
                        "1": 4
                    },
                    {
                        "1": 2
                    },
                    {
                        "1": 3
                    },
                    {
                        "1": 5
                    }
                ]
            },
            "2": {
                "1": [
                    {
                        "1": 1
                    },
                    {
                        "1": 2
                    },
                    {
                        "1": 3
                    }
                ]
            },
            "3": {
                "1": [
                    "9057251",
                    "9057255",
                    "9057273",
                    "9057298",
                    "9057307",
                    "9057289",
                    "9057284",
                    "9057293",
                    "9057300",
                    "9057291",
                    "1014969",
                    "9057286",
                    "9057295",
                    "9057302",
                    "9057261",
                    "9057279",
                    "9057299",
                    "1014966",
                    "9057254",
                    "9057301",
                    "9057292",
                    "9057256",
                    "9057283",
                    "9057249",
                    "9057303",
                    "9057294",
                    "9057260",
                    "9057278",
                    "9057296"
                ]
            }
        },
        "15": true
    }
}

 ```


## Example Links for Data Scraping
### Video   
*https://adstransparency.google.com/advertiser/AR06503673263263055873/creative/CR05870336561161175041?region=US&topic=political*  
https://adstransparency.google.com/advertiser/AR02263241812720222209/creative/CR16714562941231300609?region=US&topic=political&format=VIDEO
https://adstransparency.google.com/advertiser/AR17896267392510590977/creative/CR18102955856042655745?region=US&topic=political&format=VIDEO 

### Deleted Video
https://adstransparency.google.com/advertiser/AR11825178974693097473/creative/CR03980852629424046081?region=US&topic=political

### Video from outside source
https://adstransparency.google.com/advertiser/AR15056374268377956353/creative/CR18405671129659211777?region=US&topic=political

### Image
https://adstransparency.google.com/advertiser/AR12552007562821632001/creative/CR18385251068427632641?region=US&topic=political&format=IMAGE  
https://adstransparency.google.com/advertiser/AR05941226061533544449/creative/CR18305657421692928001?region=US&topic=political&format=IMAGE

### Text 
https://adstransparency.google.com/advertiser/AR11446901619883507713/creative/CR17595959362164097025?region=US&topic=political&format=TEXT
https://adstransparency.google.com/advertiser/AR09510539941176672257/creative/CR17071945177066635265?region=US&topic=political&format=TEXT
https://adstransparency.google.com/advertiser/AR05941226061533544449/creative/CR18305657421692928001?region=US&topic=political&format=TEXT


