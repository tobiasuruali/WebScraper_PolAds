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
           str_detect(youtube_url, "^https") &
           (str_detect(tolower(advertiser_name), "trump") | str_detect(tolower(advertiser_name), "biden")))

us_trump_video <- us_video_url_scraped %>%  
  filter(youtube_url != "NoVideo" & 
           str_detect(youtube_url, "^https") &
           str_detect(tolower(advertiser_name), "trump"))

us_biden_video <- us_video_url_scraped %>%  
  filter(youtube_url != "NoVideo" & 
           str_detect(youtube_url, "^https") &
           str_detect(tolower(advertiser_name), "biden"))

# Create a sample of 25 videos each
# Set the seed for reproducibility
set.seed(123)
# Get the number of rows in the dataset
n <- nrow(us_trump_video)
# Randomly select 25 row indices
rows <- sample(n, size = min(25, n))
# Subset the dataset using the selected row indices
us_trump_video_25 <- us_trump_video[rows, ]
us_biden_video_25 <- us_biden_video[rows, ]

saveRDS(us_trump_biden_video, "data/data_processed/data_filtered/us_trump_biden_video.Rds")
saveRDS(us_trump_video_25, "data/data_processed/data_filtered/us_trump_video_25.Rds")
saveRDS(us_biden_video_25, "data/data_processed/data_filtered/us_biden_video_25.Rds")


