import os.path
import re

import requests
import json
import time


def sanitize_filename(filename):
    # Replace or remove special characters and Unicode characters using regular expressions
    filename = re.sub(
        r'[\/:*?"<>|\x00-\x1F\x7F-\x9F]', "", filename
    )  # \x00-\x1F and \x7F-\x9F range covers most control characters
    filename = re.sub(r"\s+", "_", filename)  # Replace all types of whitespace with underscores
    # Limit filename length
    max_length = 240  # Leave some space to avoid exceeding the 260-character limit for path length
    if len(filename) > max_length:
        filename = filename[:max_length]
    return filename


# Configure API key and search parameters
api_key = ""
show = 25  # Number of results returned each time
offset = 0  # Starting position
max_results = 5000000  # Maximum number of results to retrieve

# Set request headers
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-ELS-APIKey": api_key,
}
# Construct search URL
url = "https://api.elsevier.com/content/search/sciencedirect"

down_headers = {"Accept": "application/pdf", "X-ELS-APIKey": api_key}
down_url = "https://api.elsevier.com/content/article/doi/"

query = "(silicon photonics) AND DC coupling"  # Search keywords using logical operators
files_path = "(silicon-photonics)-AND-DC-coupling"

if not os.path.exists(files_path):
    os.mkdir(files_path)

# Path to file storing the DOIs of downloaded articles
downloaded_dois_file = "downloaded_dois.txt"

# Create an empty file if it does not exist
if not os.path.exists(downloaded_dois_file):
    with open(downloaded_dois_file, "w") as f:
        pass

# Read the downloaded DOIs
with open(downloaded_dois_file, "r") as f:
    downloaded_dois = set(f.read().splitlines())


while offset < max_results:
    # Set the request body
    payload = {
        "qs": query,
        "display": {
            "offset": offset,
            "show": show,
        },
        # "filters": {
        #     "openAccess": True,
        # },
    }

    # Send PUT request and get the response
    response = requests.put(url, headers=headers, data=json.dumps(payload))

    # Process the response
    if response.status_code == 200:
        print("Responded")
        search_results = response.json()
        print(search_results)

        articles = search_results.get("results", [])

        if not articles:
            break

        for i, article in enumerate(articles, offset + 1):
            doi = article.get("doi", "DOI not available")
            if doi in downloaded_dois:
                print(f"Article already downloaded, skipping: DOI {doi}")
                continue
            title = article.get("title", "No title")
            # sanitized_title = re.sub(r'[\/:*?"<>|]', "", title)
            sanitized_title = sanitize_filename(title)
            print(f"Article {i} Title: {title}\nDOI: {doi}\n")

            # Download
            down_response = requests.get(down_url + doi, headers=down_headers)

            if down_response.status_code == 200:
                with open(
                    f"{files_path}/{sanitized_title}.pdf",
                    "wb",
                ) as file:
                    file.write(down_response.content)
                print("Article PDF downloaded successfully.")

                with open(
                    f"{files_path}/{sanitized_title}.json",
                    "w",
                    encoding="utf-8",
                ) as file_json:
                    json.dump(article, file_json, ensure_ascii=False, indent=4)

                # Write the DOI of the successfully downloaded PDF to the file
                with open(downloaded_dois_file, "a") as f:
                    f.write(doi + "\n")
            else:
                print("Failed to retrieve article:", down_response.status_code)
            time.sleep(1)
        # Update the starting position to get the next page of results
        offset += show

        # Control request frequency to avoid exceeding API limits
        time.sleep(1)
    else:
        print("Search failed:", response.status_code)
        break
