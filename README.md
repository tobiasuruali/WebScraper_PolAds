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
