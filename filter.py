import requests

def filter_businesses(businesses):
    """
    Filters a list of businesses based on the specified criteria.

    Args:
        businesses (list): A list of dictionaries, where each dictionary
                           represents a business.

    Returns:
        list: A list of dictionaries, where each dictionary represents a
              business that meets the specified criteria.
    """

    filtered_businesses = []

    for business in businesses:
        # Check if the business has a website
        if not business["Website Link"]:
            filtered_businesses.append(business)
            continue

        # Check if the website is a 404 or a redirect to a social media page
        try:
            response = requests.get(business["Website Link"], timeout=10)
            if response.status_code == 404:
                filtered_businesses.append(business)
                continue
            if "facebook.com" in response.url or "instagram.com" in response.url:
                filtered_businesses.append(business)
                continue
        except:
            filtered_businesses.append(business)
            continue

    return filtered_businesses

if __name__ == "__main__":
    # Create a list of businesses
    businesses = [
        {
            "Business Name": "Test Business 1",
            "Website Link": "https://www.google.com",
        },
        {
            "Business Name": "Test Business 2",
            "Website Link": "https://www.facebook.com",
        },
        {
            "Business Name": "Test Business 3",
            "Website Link": "",
        },
        {
            "Business Name": "Test Business 4",
            "Website Link": "https://www.asdfasdfasdf.com",
        },
    ]

    # Filter the businesses
    filtered_businesses = filter_businesses(businesses)

    # Print the filtered businesses
    for business in filtered_businesses:
        print(business)
