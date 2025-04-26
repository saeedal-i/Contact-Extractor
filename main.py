import logging
from app import app

if __name__ == "__main__":
    # Set up logging for better debugging
    logging.basicConfig(level=logging.DEBUG)
    # Run the Flask app on port 5000 and make it accessible externally
    app.run(host="0.0.0.0", port=5000, debug=True)
