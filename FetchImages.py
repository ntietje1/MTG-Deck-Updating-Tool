import os
import requests
import shutil
import json
from urllib.request import urlopen
import time as t
import string

# Check whether the specified path exists or not
def GetCardImage(card_name):
    path = os.getcwd() + "\\Images"
    if not os.path.exists(path):

        # Create a new directory because it does not exist
        os.makedirs(path)
        print("New image directory created!")
        
    if os.path.exists(path + "\\" + card_name + ".png"):
        print(card_name + ".png already downloaded! Using existing png")
        return 
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    formattedCardName = card_name.translate(translator)
    
    # Replace spaces with "-"
    formattedCardName = formattedCardName.replace(" ", "-")

    # Set up the image URL and filename
    json_url = "https://api.scryfall.com/cards/named?fuzzy={0}".format(formattedCardName)
    
    # Store the response of URL
    response = urlopen(json_url)
    
    # Storing the JSON response from url in data
    json_data = json.loads(response.read())
    
    # Retrieve the url to the card png
    image_url = json_data['image_uris']['png']
    
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream = True)
    
    # Check if the image was retrieved successfully
    filename = card_name + ".png"
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
    
        # Open a local file with wb ( write binary ) permission.
        with open(path + "\\" + filename,'wb') as f:
            shutil.copyfileobj(r.raw, f)
        
        print('Image successfully Downloaded: ',filename)
    else:
        print('Image Couldn\'t be retrieved')
    

def GetDeckImages(deck_title):
    path = os.getcwd() + "\\Decks\\" + deck_title
    
    # Check if the deck has been downloaded
    if not os.path.exists(path + ".txt"):
        print(deck_title + " not found!")
        return
    
    print(deck_title + " found!")
    
    with open(path + ".txt") as f:
        for i, line in enumerate(f):
            if i < 3:  # Skip the first 3 lines
                continue
            # Strip the card quantity and the \n character from each line
            first_space_index = line.find(' ')
            if first_space_index != -1:
                cardName = line[first_space_index+1:].strip()
                GetCardImage(cardName)
                t.sleep(0.1)
        

    
