from google_maps_scraper import scrape_google_maps
from google_search_scraper import scrape_google_search
from filter import filter_businesses
from output import output_data

def main():
    """
    Main function to run the scraper.
    """

    # Get the service and location from the user
    service = "Web Design"
    location = "New York"

    # Scrape Google Maps and Google Search
    google_maps_businesses = scrape_google_maps(service, location)
    google_search_businesses = scrape_google_search(service, location)

    # Combine the lists of businesses
    businesses = google_maps_businesses + google_search_businesses

    # Filter the businesses
    filtered_businesses = filter_businesses(businesses)

    # Output the data in CSV and JSON format
    output_data(filtered_businesses, "csv")
    output_data(filtered_businesses, "json")

if __name__ == "__main__":
    main()
