library(tidyverse)

# Read all the scraped batch files and combine into one df
us_video_url_scraped <- list.files(
  path = "data/data_raw/auto_batch/",
  pattern = "*.Rds",
  full.names = TRUE
) %>% map_dfr(readRDS)


## Only work with Biden or Trump Advertisers 

us_trump_biden_video <- us_video_url_scraped %>%  
  filter(youtube_url != "NoVideo" & 
           (str_detect(tolower(advertiser_name), "trump") | str_detect(tolower(advertiser_name), "biden")))
