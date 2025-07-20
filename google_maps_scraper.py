import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_google_maps(service, location):
    """
    Scrapes Google Maps for businesses based on a service and location.

    Args:
        service (str): The service to search for (e.g., "Web Design").
        location (str): The location to search in (e.g., "New York").

    Returns:
        list: A list of dictionaries, where each dictionary represents a business
              and contains the business's name, category, address, email, phone,
              Google Maps link, and website link.
    """

    # Create a new instance of the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # Go to the Google Maps website
    driver.get("https://www.google.com/maps")

    # Find the search box and enter the search query
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(f"{service} in {location}")
    search_box.submit()

    # Wait for the search results to load
    time.sleep(5)

    # Get the search results
    search_results = driver.find_elements(By.CLASS_NAME, "Nv2PK")

    # Create a list to store the scraped data
    scraped_data = []

    # Loop through the search results and extract the data
    for result in search_results:
        try:
            # Get the business name
            name = result.find_element(By.CLASS_NAME, "qBF1Pd").text

            # Get the business category
            category = result.find_element(By.CLASS_NAME, "vVAdxe").text

            # Get the business address
            address = result.find_element(By.CLASS_NAME, "vVAdxe").text

            # Get the business phone number
            try:
                phone = result.find_element(By.CLASS_NAME, "vVAdxe").text
            except:
                phone = ""

            # Get the business website
            try:
                website = result.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                website = ""

            # Get the Google Maps link
            google_maps_link = result.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Create a dictionary to store the data
            data = {
                "Business Name": name,
                "Industry Category": category,
                "Address": address,
                "Email": "",
                "Phone": phone,
                "Google Maps Link": google_maps_link,
                "Website Link": website,
            }

            # Add the data to the list
            scraped_data.append(data)
        except Exception as e:
            print(f"Error scraping result: {e}")

    # Close the browser
    driver.quit()

    return scraped_data

if __name__ == "__main__":
    # Scrape Google Maps
    scraped_data = scrape_google_maps("Web Design", "New York")

    # Print the scraped data
    for data in scraped_data:
        print(data)
