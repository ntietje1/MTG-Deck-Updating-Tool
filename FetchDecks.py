from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import re
import os
from datetime import datetime
import shutil

# Convert text file into a dictionary with card names as keys and quantity as value
def MakeCardDict(text_path):
    CardDict = {}
    with open(text_path, 'r') as file:
        for i, line in enumerate(file):
                # Get the quantity and the name of each card
                colon_index = line.find(':')
                if colon_index != -1:
                    # Add the card to the dictionary
                    cardName = line[:colon_index]
                    cardQuantity = int(line[colon_index+1:].strip())
                    CardDict[cardName] = cardQuantity
                    #print("Added " + cardName + " to dictionary!")
    
    return CardDict
    

# Scrape a moxfield profile for public decks and retrieve deck lists for each found
def UpdateCurrentDecks(profile_url):
    # if the user only entered their username, turn it into their profile url
    if (profile_url[0:8] != "https://"):
        profile_url = "https://www.moxfield.com/users/" + profile_url + "/decks/public"

    # Check whether the specified path exists or not
    path = os.getcwd() + "\\Decks"
    if not os.path.exists(path):

        # Create a new directory because it does not exist
        os.makedirs(path)
        print("New deck directory created!")

    # Disable the browser window opening
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')

    # Create the Firefox driver
    browser = webdriver.Firefox(options=options)
    url = profile_url
    browser.get(url)

    # Wait for an element with class "deckbox" to be present
    print("Searching for decks...")
    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "deckbox")))
    source = browser.page_source
    soup = bs(source, "html.parser")

    # Store all found deck titles and links
    decks = []
    count = 0
    deckboxes = soup.find_all('a', class_='deckbox')
    for deckbox in deckboxes:
        count = count + 1
        deck_link = "https://www.moxfield.com/embed" + deckbox['href'][6:]
        deck_title = deckbox.find('span', class_='deckbox-title').text
        decks.append((deck_title, deck_link))
    print("Found " + str(count) + " decks!")

    # Define the pattern to search for card name and quantity
    pattern = r'<td class="text-end">(\d+)</td><td><a class="text-body cursor-pointer no-outline" tabindex="0">([^<]+)</a></td>'

    # For every deck found, grab all cards and write to the text file       
    for deck in decks:
        f = open(path + "\\" + deck[0] + ".txt", "w+")
        print("Opened " + deck[0] + ".txt")
        #f.write(deck[0] + "\n")
        #f.write(deck[1] + "\n")
        #f.write("Retrieved on: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n")
        
        url = deck[1]
        browser.get(url)
        
        # Wait for page to load fully
        wait = WebDriverWait(browser, 10)
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-deck-row")))
        source = browser.page_source
        soup = bs(source, "html.parser")

        # Use regular expressions to find all matches
        matches = re.findall(pattern, str(soup))

        # Write the quantity and name for each match
        count = 0
        for match in matches:
            card_amount, card_name = match
            f.write(card_name + ":" + card_amount + "\n")
            count = count + int(card_amount)
        print("Successfully added " + str(count) + " cards!")
        
        # Close the text file    
        f.close()

    # Close the browser
    browser.quit()

# Keep a copy of the current decks to use as reference in the future    
def SaveDecks():
    # Delete existing save if there is one
    path = os.getcwd() + "\\SavedDecks"
    if os.path.exists(path):
        shutil.rmtree(path)
    
    # Copy over current decks    
    source_dir = os.getcwd() + "\\Decks"
    destination_dir = os.getcwd() + "\\SavedDecks"
    shutil.copytree(source_dir, destination_dir)
    
# Find all changes made to specific deck since last save created    
def CompareDecks(fileName):
    # Check whether the specified path exists or not
    path1 = os.getcwd() + "\\Decks\\" + fileName
    path2 = os.getcwd() + "\\SavedDecks\\" + fileName
    if not os.path.exists(path1): 
        print("Deck not found in current decks!")
        return
    if not os.path.exists(path2):
        print("Deck not found in saved decks!")
        saved_deck = {}
    else:
        saved_deck = MakeCardDict("SavedDecks\\" + fileName)
    
    # Convert text files into dictionaries
    current_deck = MakeCardDict("Decks\\" + fileName)
    
    # Find differences in the dictionaries
    diff_dict = {k: current_deck.get(k, 0) - saved_deck.get(k, 0) for k in set(saved_deck) | set(current_deck)}
    
    # Create a new dictionary with only the non-zero entries
    diff_dict_no_zeros = {k: v for k, v in diff_dict.items() if v != 0}
    
    print("Changes made to " + fileName + " found:")
    print(diff_dict_no_zeros)
    
    return diff_dict_no_zeros
                    

# Find all changes made to all decks since last save created
def CompareAllDecks():
    for deck_title in os.listdir("Decks//"):
        if deck_title.endswith('.txt'):
            diff_dict = CompareDecks(deck_title)