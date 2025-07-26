# El País Cross-Browser Article Scraper and Analyzer

This project provides a Python-based solution for scraping opinion articles from the El País newspaper, translating their headlines, and analyzing word frequencies across different browser environments using Selenium and BrowserStack.

## Prerequisites

- Python 3.x
- BrowserStack Account (with Username and Access Key)
- RapidAPI Key (for Google Translate API)

## How to Run

1. Clone the repository:

    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name

2. Install Dependencies:

    Install the required Python packages using pip:

    pip install -r requirements.txt

3. Configure API Keys and Credentials:

    - BrowserStack:
      Open `cross_browser_test_runner.py` and replace the placeholder values with your actual BrowserStack credentials:

        BROWSERSTACK_USERNAME = 'your_browserstack_username'
        BROWSERSTACK_ACCESS_KEY = 'your_browserstack_access_key'

    - RapidAPI (Google Translate):
      Open `elpais_scraper.py` and replace the placeholder with your RapidAPI key:

        RAPIDAPI_KEY = "your_rapidapi_key"

4. Execute the Script:

    Run the `cross_browser_test_runner.py` script directly:

    python cross_browser_test_runner.py

    This will initiate the cross-browser tests on BrowserStack, and you will see the progress and results printed to your console.
