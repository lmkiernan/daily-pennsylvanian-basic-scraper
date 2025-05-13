"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys

import daily_event_monitor

import bs4
import requests
import loguru


def scrape_first_sports_headline():
    url = "https://www.thedp.com/section/sports"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.ok:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        first_article = soup.find("div", class_="row section-article")
        if first_article:
            headline_tag = first_article.find("h3", class_="standard-link")
            if headline_tag and headline_tag.a:
                return headline_tag.a.text.strip()
    return ""


if __name__ == "__main__":

    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        headline = scrape_first_sports_headline()
        print("First Sports Headline:", headline)
    except Exception as e:
        loguru.logger.error(f"Failed to scrape data point: {e}")
        headline = None

    # Save data
    if headline is not None:
        dem.add_today(headline)
        dem.save()
        loguru.logger.info("Saved daily event monitor")

    def print_tree(directory, ignore_dirs=[".git", "__pycache__"]):
        loguru.logger.info(f"Printing tree of files/dirs at {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * (level)
            loguru.logger.info(f"{indent}+--{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                loguru.logger.info(f"{sub_indent}+--{file}")

    print_tree(os.getcwd())

    if os.path.exists(dem.file_path):
        with open(dem.file_path, "r") as f:
            loguru.logger.info(f.read())
    else:
        loguru.logger.info(f"File {dem.file_path} does not exist yet.")

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")
