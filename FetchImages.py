import os
import requests
import shutil
import json
from urllib.request import urlopen
import time as t

# Fix bad file names
def FormatCardName(card_name):
    formattedCardName = card_name.replace("\"", "") # Delete slashes
    formattedCardName = card_name.replace("/", "") # Delete slashes
    formattedCardName = formattedCardName.replace(" ", "-") # Replace spaces 
    formattedCardName = formattedCardName.replace(",", "") # Delete commas
    formattedCardName = formattedCardName.replace("\"", "") # Delete quotes
    formattedCardName = formattedCardName.replace("\'", "") # Delete quotes
    formattedCardName = formattedCardName.lower()
    return formattedCardName

def getPrintings(card_name):
    
    formattedCardName = FormatCardName(card_name)
    
    # Search for card using Scryfall API
    json_url = "https://api.scryfall.com/cards/named?fuzzy={0}".format(formattedCardName)
    response = requests.get(json_url)
    card_info = response.json()

    # Retrieve the prints_search_uri
    prints_search_uri = card_info.get("prints_search_uri")
    if not prints_search_uri:
        return None
    
    # Detect if the card is dual faced
    if card_info['layout'] in ["modal_dfc", "transform"]:
        dual_faced = True
    else:
        dual_faced = False

    # Get the printings for the card
    response = requests.get(prints_search_uri)
    printings_info = response.json()
    
    printings = []
    image_uris = []
    formattedCardNames = []
    if not dual_faced:
        formattedCardNames = [formattedCardName]
        
        # Add the default printing of the card to the list
        default_printing = {}
        default_printing["formattedCardNames"] = formattedCardNames
        default_printing["set_name"] = "DEFAULT SET"
        default_printing["set_code"] = "DEF"
        default_printing["collector_num"] = "-1"
        default_printing["image_uris"] = [card_info['image_uris']['png']]
        printings.append(default_printing)
        
        # Parse the printing information and store it in a list
        for printing in printings_info["data"]:
            new_printing = {}
            new_printing["formattedCardNames"] = formattedCardNames
            new_printing["set_name"] = printing["set_name"]
            new_printing["set_code"] = printing["set"]
            new_printing["collector_num"] = printing["collector_number"]
            new_printing["image_uris"] = [printing["image_uris"]["png"]]
            printings.append(new_printing)
    
    else: # If dual faced:
        # Split the card name into two halves
        split_index = formattedCardName.find("--")
        formattedCardNames = [formattedCardName[:split_index], formattedCardName[split_index+2:]]
        
        # Add the default printing of the card to the list
        default_image_uris = []
        for i in range (0,2): # Split card name and get 2 image urls
            default_image_uris.append(card_info['card_faces'][i]['image_uris']['png'])
        
        default_printing = {}
        default_printing["formattedCardNames"] = formattedCardNames
        default_printing["set_name"] = "DEFAULT SET"
        default_printing["set_code"] = "DEF"
        default_printing["collector_num"] = "-1"
        default_printing["image_uris"] = default_image_uris
        printings.append(default_printing)
        
        # Parse the printing information and store uris for both faces in a list
        for printing in printings_info["data"]:
            image_uris = []
            for i in range (0,2): # Split card name and get 2 image urls
                image_uris.append(printing["card_faces"][i]["image_uris"]["png"])
            
            new_printing = {}
            new_printing["formattedCardNames"] = formattedCardNames
            new_printing["set_name"] = printing["set_name"]
            new_printing["set_code"] = printing["set"]
            new_printing["collector_num"] = printing["collector_number"]
            new_printing["image_uris"] = image_uris
            printings.append(new_printing)
            
    print(printings)
    return printings

# If a card is double faced, split the card name in 2 and make two scryfall api requests
# Return a list of card names and image uris (will be length 1 most of the time)
# Note: there is a slightly better way to directly request the image uris
def splitCardName(card_name):
    formattedCardName = FormatCardName(card_name)
    
    # Set up the image URL and filename
    json_url = "https://api.scryfall.com/cards/named?fuzzy={0}".format(formattedCardName)
    
    # Store the response of URL
    print("attempting to retrieve: " + json_url)
    response = urlopen(json_url)
    
    # Storing the JSON response from url in data
    json_data = json.loads(response.read())
    
    # Retrieve the url to the card png
    image_urls = []
    if json_data['layout'] in ["modal_dfc", "transform"]: # Check if the card is dual faced
        for i in range (0,2): # Split card name and get 2 image urls
            image_urls.append(json_data['card_faces'][i]['image_uris']['png'])
            split_index = formattedCardName.find("--")
            formattedCardNames = [formattedCardName[:split_index], formattedCardName[split_index+2:]]
    else:
        image_urls.append(json_data['image_uris']['png'])
        formattedCardNames = [formattedCardName]
    
    print("Retrieved image uri: ")
    print(image_urls)
    return (formattedCardNames, image_urls)

# Retrieve a single card image from scryfall's api
def GetCardImage(card_name):
    # Check whether the specified path exists or not
    path = os.getcwd() + "\\Images"
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("New image directory created!")
        
    # Split dual faced cards and retrieve all image urls as lists
    retrieved_data = splitCardName(card_name)
    formattedCardNames = retrieved_data[0]
    image_urls = retrieved_data[1]
    
    # Check if the image/images have already been downloaded
    # This might not work if one half of a dual faced card was downloaded (probably won't happen)
    for f_card_name in formattedCardNames:
        if os.path.exists(path + "\\" + f_card_name + ".png"):
            print(f_card_name + ".png already downloaded! Using existing png")
            return 
    
    # Open the url image, set stream to True, this will return the stream content.
    for image_url, name in zip(image_urls, formattedCardNames):
        r = requests.get(image_url, stream = True)
    
        # Check if the image was retrieved successfully
        filename = name + ".png"
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
        
            # Open a local file with wb ( write binary ) permission.
            with open(path + "\\" + filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
            
            print('Image successfully Downloaded: ',filename)
        else:
            print('Image Couldn\'t be retrieved')
    
# Retrieve an entire deck's images from scryfall's api
def GetDeckImages(deck_title):
    path = os.getcwd() + "\\Decks\\" + deck_title
    
    # Check if the deck has been downloaded
    if not os.path.exists(path):
        print(deck_title + " not found!")
        return
    
    print(deck_title + " found!")
    
    # Read each line of the text file and extract the card names only
    with open(path) as f:
        for i, line in enumerate(f):
            # Strip the card quantity and the \n character from each line
            colon_index = line.find(':')
            if colon_index != -1:
                card_name = line[:colon_index]
                GetCardImage(card_name)
                t.sleep(0.1)
                
# Retrieve all images for a dictionary of cards from scryfall's api
def GetAllImages(card_dict):
    for card_name, card_quantity in card_dict.items():
        if card_quantity > 0:
            GetCardImage(card_name)
            

            
        

    
