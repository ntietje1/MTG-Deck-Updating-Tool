from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re

# Disable the browser window opening
options = webdriver.FirefoxOptions()
options.add_argument('-headless')

# Create the Firefox driver
browser = webdriver.Firefox(options=options)
url = 'https://www.moxfield.com/embed/EDtSi9QS9UKj8d9RahGTMw'
browser.get(url)
source = browser.page_source
soup = bs(source, "html.parser")

# Define the pattern to search for the title
title_pattern = r'<h3 class="mb-0"><strong>([^<]+)</strong></h3>'

# Use regular expressions to find all matches
title_match = re.search(title_pattern, str(soup))

# Print the title of the deck
if title_match:
    title = title_match.group(1)
    print(title)

# Define the pattern to search for card name and quantity
pattern = r'<td class="text-end">(\d+)</td><td><a class="text-body cursor-pointer no-outline" tabindex="0">([^<]+)</a></td>'

# Use regular expressions to find all matches
matches = re.findall(pattern, str(soup))

# Print the quantity and name for each match
for match in matches:
    card_amount, card_name = match
    print(card_amount, card_name)

# Close the browser
browser.quit()