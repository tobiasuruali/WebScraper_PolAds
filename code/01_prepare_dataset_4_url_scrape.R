library(tidyverse) 


google_pol_ads <- readRDS("data/data_processed/google_pol_ads.Rds")

# For scrape processing we only need a subset of the full data
# Select the ad_id, ad_url filter only the "US" regions and "VIDEO"
us_video_rows <- google_pol_ads %>%
   filter(str_detect(regions, "US") & ad_type == "VIDEO" &
            #Filter out HBO ads (not political)
            advertiser_name != "HOME BOX OFFICE, INC.") %>%
   select(ad_id,date_range_start, ad_url, advertiser_id, advertiser_name) %>%
   arrange((date_range_start))


saveRDS(us_video_rows, "data/data_processed/us_video_ads.Rds")


