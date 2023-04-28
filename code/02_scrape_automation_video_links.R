library(tidyverse)
library(RSelenium)
library(crayon)
library(fst)

us_video_rows <- read_fst("data/data_processed/us_video_ads.fst")


# Function to start RSelenium
start_rselenium <- function() {
  message("Starting RSelenium...")
  # Headless Firefox browser improves performance
  exCap <- list("moz:firefoxOptions" = list(args = list('--headless')))
  remDr <- RSelenium::remoteDriver(remoteServerAddr = "localhost",
                                   port = 4445L,
                                   browserName = "firefox",
                                   extraCapabilities = exCap
                                   )
  remDr$open()
  remDr
}

# Start RSelenium
remDr <- start_rselenium()

# Create a new column to store the YouTube URLs
us_video_rows$youtube_url <- NA

# Define the amount of video_urls that should be scraped before
# saving the data to a file
# RSelenium had issues with scraping more than 16 URLs at a time before crashing
batch_size <- 16

# Generate a vector of row indices that have not been processed yet
# For the first time, run this code:

# unprocessed_rows <- seq_len(nrow(us_video_rows))
# Get the unprocessed row vector (saved in the function below)

# 2nd time onwards, run this code:
unprocessed_rows <- readRDS("data/data_processed/log/unprocessed_rows.Rds")


#Generate number of rows processed first time = 0, after the difference between total rows - unprocessed rows
#For the first time, run this code:
# total_rows_processed <- 0

# 2nd time onwards, run this code:
total_rows_processed <- as.numeric(nrow(us_video_rows) - length(unprocessed_rows))


# Initialize a counter variable
iteration_count <- 0

# Set the maximum number of iterations
max_iterations <- 32

while (length(unprocessed_rows) > 0 && iteration_count < max_iterations) {
  # Generate a random sample of row indices for this batch
  message("Generating random sample of row indices for this batch...")
  message(cyan(paste("Number of unprocessed rows: ", length(unprocessed_rows))))
  # Batch rows are a random sample of the unprocessed rows
  batch_rows <- sample(unprocessed_rows, min(batch_size, length(unprocessed_rows)))
  
  for (row_index in batch_rows) {
    # Navigate to the ad URL
    remDr$navigate(us_video_rows$ad_url[row_index])
    
    # Pause for 3.5 seconds to allow the page to load
    Sys.sleep(3)
    
    # Try to find the iframe element and switch into it
    tryCatch({
      video_elem <- remDr$findElement(
        using = "css selector", "iframe[src*='youtube.com']")
      remDr$switchToFrame(video_elem)
      
      # Extract the href attribute from the ytp-impression-link element
      ytp_impression_link <- remDr$findElement(
        using = "css selector", ".ytp-impression-link")
      youtube_link <- ytp_impression_link$getElementAttribute("href")
      
      # Store the extracted YouTube URL in the youtube_url column
      us_video_rows$youtube_url[row_index] <- youtube_link[[1]]
      message(green(paste("Success: Row",row_index,": ", youtube_link[[1]])))
    }, error = function(e) {
      # If an error occurs (e.g. iframe element not found), store "NoVideo" in the youtube_url column and print an error message
      us_video_rows$youtube_url[row_index] <<- "NoVideo"
      message(paste("Error: Row", row_index, "had no video available."))
      
      # Write the row id and ad_id to a error text file
      write(paste(row_index, us_video_rows$ad_id[row_index], us_video_rows$advertiser_name[row_index],
                  us_video_rows$ad_url[row_index]),
            file = "data/data_processed/log/error_rows_auto_us_video_scrape.txt", append = TRUE)
    })
    
  }
  
  total_rows_processed <<- total_rows_processed + length(batch_rows)
    # Save data to RDS files
  message("Saving data to RDS files...")
  processed_rows <- us_video_rows[batch_rows, ]
  saveRDS(processed_rows, paste0("data/data_raw/auto_batch/us_video_ads_", total_rows_processed, ".Rds"))
  
  # Print message showing how many rows have been processed so far
  message(yellow(paste(total_rows_processed, "rows processed so far...")))
  

  # Remove processed rows from unprocessed_rows vector
  unprocessed_rows <<- setdiff(unprocessed_rows, batch_rows)
  
  # Save unprocessed rows to RDS file
  saveRDS(unprocessed_rows, "data/data_processed/log/unprocessed_rows.Rds")
  
  # Restart RSelenium every time the batch of 16 is processed
  # Close RSelenium once last iteration was reached
  if (iteration_count < max_iterations - 1) {
    message(magenta$bold(paste("Closing and restarting RSelenium...")))
    remDr$close()
    remDr <- start_rselenium()
  } else {
    message(red$bold(paste("Closing RSelenium...")))
    remDr$close()
  }
  
  # Increment the counter variable at the end of each iteration
  iteration_count <<- iteration_count + 1
  message(magenta$bold(paste("Starting Iteration: ", iteration_count, "...")))

}

# Close RSelenium
message("Closing RSelenium...")
remDr$close()
