import csv
import json

def output_data(data, format):
    """
    Outputs the scraped data in either CSV or JSON format.

    Args:
        data (list): A list of dictionaries, where each dictionary represents a
                     business.
        format (str): The format to output the data in ("csv" or "json").
    """

    if not data:
        return

    if format == "csv":
        with open("output.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    elif format == "json":
        with open("output.json", "w") as f:
            json.dump(data, f, indent=4)

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
    ]

    # Output the data in CSV format
    output_data(businesses, "csv")

    # Output the data in JSON format
    output_data(businesses, "json")
