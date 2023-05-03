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

def splitCardName(card_name):
    f_card_name = FormatCardName(card_name)
    split_index = f_card_name.find("--")
    formattedCardName = f_card_name[:split_index]
    return formattedCardName

def getPrintings(card_name):
    
    formattedCardName = FormatCardName(card_name)
    
    # Search for card using Scryfall API
    print("going to url: https://api.scryfall.com/cards/named?fuzzy={0}".format(formattedCardName))
    json_url = "https://api.scryfall.com/cards/named?fuzzy={0}".format(formattedCardName)
    response = requests.get(json_url)
    card_info = response.json()

    # Retrieve the prints_search_uri
    prints_search_uri = card_info.get("prints_search_uri")
    if not prints_search_uri:
        print("print search uri not found!!!")
        return None
    
    # Detect if the card is dual faced
    dual_faced = card_info['layout'] in ["modal_dfc", "transform"]

    # Get the printings for the card
    response = requests.get(prints_search_uri)
    printings_info = response.json()
    
    printings = {}
    image_uris = []
    formattedCardNames = []
    if not dual_faced:
        formattedCardNames = [formattedCardName]
        
        # Add the default printing of the card to the list
        default_printing = {}
        default_printing["formattedCardNames"] = formattedCardNames
        default_printing["set_name"] = "DEFAULT SET"
        default_printing["set_code"] = "def"
        default_printing["collector_num"] = "-1"
        default_printing["image_uris"] = [card_info['image_uris']['png']]
        default_printing["dual_faced"] = "False"
        default_printing["default"] = "True"
        printings["def"] = default_printing
        
        # Parse the printing information and store it in a list
        for printing in printings_info["data"]:
            new_printing = {}
            new_printing["formattedCardNames"] = formattedCardNames
            new_printing["set_name"] = printing["set_name"]
            new_printing["set_code"] = printing["set"]
            new_printing["collector_num"] = printing["collector_number"]
            new_printing["image_uris"] = [printing["image_uris"]["png"]]
            new_printing["dual_faced"] = "False"
            new_printing["default"] = "False"
            printings[printing["set"]] = new_printing
    
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
        default_printing["set_code"] = "def"
        default_printing["collector_num"] = "-1"
        default_printing["image_uris"] = default_image_uris
        default_printing["dual_faced"] = "True"
        default_printing["default"] = "True"
        printings["def"] = default_printing
        
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
            new_printing["dual_faced"] = "True"
            new_printing["default"] = "False"
            printings[printing["set"]] = new_printing
            
    #print(printings)
    #t.sleep(0.1)
    return printings

# Retrieve a single card image from scryfall's api
def GetCardImage(card_name, **kwargs):
    # Check whether the specified path exists or not
    path = os.getcwd() + "\\Images"
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("New image directory created!")
        
    set_code = "def"
    for key,value in kwargs.items():
        if key == "set_code":
            set_code = value.lower()
            print("set code received!", set_code)
            
        
    # Split dual faced cards and retrieve all image urls as lists
    printings = getPrintings(card_name)
    #print(printings)
    try:
        formattedCardNames = printings.get(set_code).get("formattedCardNames")
        image_urls = printings.get(set_code).get("image_uris")
    except AttributeError as e:
        # handle the AttributeError
        print("No printing of " + card_name + " found from set: " + set_code)
        formattedCardNames = []
        image_urls = []
    
    # Check if the image/images have already been downloaded
    # This might not work if one half of a dual faced card was downloaded (probably won't happen)
    for f_card_name in formattedCardNames:
        if os.path.exists(path + "\\" + f_card_name + "-" + set_code + ".png"):
            print(f_card_name + "-" + set_code + ".png already downloaded! Using existing png")
            return printings
    
    # Open the url image, set stream to True, this will return the stream content.
    for image_url, name in zip(image_urls, formattedCardNames):
        r = requests.get(image_url, stream = True)
    
        # Check if the image was retrieved successfully
        filename = name + "-" + set_code + ".png"
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
        
            # Open a local file with wb ( write binary ) permission.
            with open(path + "\\" + filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
            
            print('Image successfully Downloaded: ',filename)
        else:
            print('Image Couldn\'t be retrieved')
    return printings
    
# # Retrieve an entire deck's images from scryfall's api
# def GetDeckImages(deck_title):
#     path = os.getcwd() + "\\Decks\\" + deck_title
    
#     # Check if the deck has been downloaded
#     if not os.path.exists(path):
#         print(deck_title + " not found!")
#         return
    
#     print(deck_title + " found!")
    
#     # Read each line of the text file and extract the card names only
#     with open(path) as f:
#         for i, line in enumerate(f):
#             # Strip the card quantity and the \n character from each line
#             colon_index = line.find(':')
#             if colon_index != -1:
#                 card_name = line[:colon_index]
#                 GetCardImage(card_name)
#                 t.sleep(0.1)
                
# Retrieve all images for a dictionary of cards from scryfall's api
def GetAllImages(card_dict):
    all_card_printings = {}
    for card_name, card_quantity in card_dict.items():
        if card_quantity > 0:
            printing = GetCardImage(card_name)
            if printing.get("dual_faced") == "False":
                FormatCardName = FormatCardName(card_name)
            else:
                FormatCardName = splitCardName(card_name)
                
            all_card_printings[card_name] = printing
            t.sleep(0.1)
    return all_card_printings        

            
        

    
