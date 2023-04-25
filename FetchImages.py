import os
import requests
import shutil
import json
from urllib.request import urlopen
import time as t
import string
import Utils as u

# Retrieve a single card image from scryfall's api
def GetCardImage(card_name):
    # Check whether the specified path exists or not
    path = os.getcwd() + "\\Images"
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("New image directory created!")
        
    formattedCardName = u.FormatCardName(card_name)
    if os.path.exists(path + "\\" + formattedCardName + ".png"):
        print(card_name + ".png already downloaded! Using existing png")
        return 
    
    # Set up the image URL and filename
    json_url = "https://api.scryfall.com/cards/named?fuzzy={0}".format(formattedCardName)
    
    # Store the response of URL
    print("attempting to retrieve: " + json_url)
    response = urlopen(json_url)
    
    # Storing the JSON response from url in data
    json_data = json.loads(response.read())
    
    # Retrieve the url to the card png
    # TODO: FIX DOUBLE FACED CARDS!!!
    # https://api.scryfall.com/cards/named?fuzzy=Etali-Primal-Conqueror--Etali-Primal-Sickness
    
    # Check if the "card_faces" field is present in the data
    # If so, split card name and get 2 image urls
    image_urls = []
    
    if json_data['layout'] in ["modal_dfc", "transform"]:
        for i in range (0,2):
            image_urls.append(json_data['card_faces'][i]['image_uris']['png'])
            split_index = formattedCardName.find("--")
            formattedCardNames = [formattedCardName[:split_index], formattedCardName[split_index+2:]]
    else:
        image_urls.append(json_data['image_uris']['png'])
        formattedCardNames = [formattedCardName]
    
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
                
# Retrieve all deck's images from scryfall's api
def GetAllImages():
    for deck_title in os.listdir("Decks//"):
        if deck_title.endswith('.txt'):
            GetDeckImages(deck_title)
            
        

    
