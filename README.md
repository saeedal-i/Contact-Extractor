# Google Maps and Google Search Scraper

This is a Python script that scrapes Google Maps and Google Search for businesses based on a service and location. It then filters the results based on whether the business has a website, if the website is a 404, or if it redirects to a social media page. Finally, it outputs the data in either CSV or JSON format.

## Features

-   Scrapes Google Maps and Google Search for businesses.
-   Filters the results based on whether the business has a website.
-   Outputs the data in either CSV or JSON format.

## How to Run

1.  Install the dependencies:
    ```
    pip install -r requirements.txt
    pip install selenium
    sudo apt-get update && sudo apt-get install -y chromium-driver
    ```
2.  Run the application:
    ```
    python main_scraper.py
    ```

## Files

-   `main_scraper.py`: The main script to run the scraper.
-   `google_maps_scraper.py`: Scrapes Google Maps for businesses.
-   `google_search_scraper.py`: Scrapes Google Search for businesses.
-   `filter.py`: Filters the scraped data.
-   `output.py`: Outputs the data in either CSV or JSON format.
-   `output.csv`: The output of the scraper in CSV format.
-   `output.json`: The output of the scraper in JSON format.
