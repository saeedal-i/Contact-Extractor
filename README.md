# Website Contact Extractor

This is a Flask web application that scrapes a website and extracts contact information such as email addresses, phone numbers, and social media links.

## Features

-   Extracts email addresses, phone numbers, and social media links from a website.
-   Crawls the website to a specified depth to find more contact information.
-   Exports the extracted data to a CSV file.
-   Error handling and retries to make the scraper more reliable.

## How to Run

1.  Install the dependencies:
    ```
    pip install -r requirements.txt
    ```
2.  Run the application:
    ```
    python main.py
    ```
3.  Open your browser and go to `http://localhost:5000`.

## API Endpoints

-   `POST /api/extract`: Extracts contact information from a website.
    -   `url`: The URL of the website to scrape.
    -   `crawl_depth`: The depth to crawl the website (0, 1, or 2).
-   `POST /api/export-csv`: Exports the extracted contact information to a CSV file.
    -   The body of the request should be the JSON response from the `/api/extract` endpoint.
