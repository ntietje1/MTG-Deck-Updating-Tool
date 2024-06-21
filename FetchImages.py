import os
import requests
import shutil
import json
from urllib.request import urlopen
import time as t


def generateFileName(card_name, id):
    return card_name + "-" + id + ".png"

# Fix bad file names


def FormatCardName(card_name):
    formattedCardName = card_name.replace("\"", "")  # Delete slashes
    formattedCardName = card_name.replace("/", "")  # Delete slashes
    formattedCardName = formattedCardName.replace(" ", "-")  # Replace spaces
    formattedCardName = formattedCardName.replace(",", "")  # Delete commas
    formattedCardName = formattedCardName.replace("\"", "")  # Delete quotes
    formattedCardName = formattedCardName.replace("\'", "")  # Delete quotes
    formattedCardName = formattedCardName.lower()
    return formattedCardName


def splitCardName(card_name):
    f_card_name = FormatCardName(card_name)
    # Split the card name into two halves
    split_index = f_card_name.find("--")
    if split_index != -1:
        formattedCardNames = [f_card_name[:split_index],
                              f_card_name[split_index+2:]]
    else:
        formattedCardNames = [f_card_name]
    return formattedCardNames


def getPrintings(card_name):

    try:
        formattedCardName = FormatCardName(card_name)

        # Search for card using Scryfall API
        # print("going to url: https://api.scryfall.com/cards/named?fuzzy={0}".format(formattedCardName))
        json_url = "https://api.scryfall.com/cards/named?fuzzy={0}".format(
            formattedCardName)
        response = requests.get(json_url)
        card_info = response.json()

        # Retrieve the prints_search_uri
        prints_search_uri = card_info.get("prints_search_uri")
        if not prints_search_uri:
            print("print search uri not found!!!")
            return None

        # Detect if the card is dual faced
        dual_faced = "card_faces" in card_info
        # card_info['layout'] in ["modal_dfc", "transform"] or

        # Get the printings for the card
        response = requests.get(prints_search_uri)
        printings_info = response.json()

        printings = {}
        image_uris = []
        formattedCardNames = splitCardName(card_info["name"])

        try:
            # Gather default printing data
            default_image_uris = []
            if dual_faced:
                for i in range(0, 2):
                    default_image_uris.append(
                        card_info['card_faces'][i]['image_uris']['png'])
            else:
                default_image_uris = [card_info['image_uris']['png']]
        except KeyError as e:
            print(f"Error while parsing card_info for default_image_uris: {e}")

        # Add the default printing of the card to the list
        try:
            default_printing = {}
            default_printing["full_name"] = FormatCardName(card_info["name"])
            default_printing["formattedCardNames"] = formattedCardNames
            default_printing["set_name"] = card_info["set_name"]
            default_printing["set_code"] = card_info["set"]
            default_printing["collector_num"] = card_info["collector_number"]
            default_printing["image_uris"] = default_image_uris
            default_printing["dual_faced"] = str(dual_faced)
            default_printing["default"] = "True"
            default_printing["unique_id"] = default_printing["set_code"] + \
                "-" + str(default_printing["collector_num"])
            printings[default_printing["unique_id"]] = default_printing
        except KeyError as e:
            print(f"Error while creating default_printing: {e}")

        # Parse the printing information and store it in a list
        try:
            for printing in printings_info["data"]:
                new_printing = {}
                new_printing["full_name"] = FormatCardName(card_info["name"])
                new_printing["formattedCardNames"] = formattedCardNames
                new_printing["set_name"] = printing["set_name"]
                new_printing["set_code"] = printing["set"]
                new_printing["collector_num"] = printing["collector_number"]
                new_printing["dual_faced"] = str(dual_faced)
                new_printing["default"] = "False"
                new_printing["unique_id"] = new_printing["set_code"] + \
                    "-" + str(new_printing["collector_num"])
        except KeyError as e:
            print(f"Error while parsing printings_info: {e}")

            if dual_faced:
                image_uris = []
                for i in range(0, 2):
                    image_uris.append(
                        printing["card_faces"][i]["image_uris"]["png"])
                new_printing["image_uris"] = image_uris
            else:
                new_printing["image_uris"] = [printing["image_uris"]["png"]]

            if new_printing["unique_id"] != default_printing["unique_id"]:
                printings[new_printing["unique_id"]] = new_printing

        return printings

    except Exception as e:
        print("Error getting printings for card: " +
              card_name + "\n" + json.dumps(card_info) + "\n" + str(e))
        return {}

# Retrieve a single card image from scryfall's api


def GetCardImage(card_name, **kwargs):
    # Check whether the specified path exists or not
    path = os.path.join(os.getcwd(), "Images")
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("New image directory created!")

    id = ""
    printings_cache = {}
    alternatePrinting = False
    # If an id was given, update the id
    for key, value in kwargs.items():
        if key == "id":
            id = value
            alternatePrinting = True
        if key == "printings_cache":
            printings_cache = value

    # Get the printings of the card
    if card_name not in printings_cache:  # Utilize cached data if possible
        printings = getPrintings(card_name)
    else:
        printings = printings_cache[card_name]

    if not alternatePrinting:
        id = list(printings.keys())[0]  # get first (default) key

    # Retrieve the name and uri lists
    try:
        formattedCardNames = printings.get(id).get("formattedCardNames")
        image_uris = printings.get(id).get("image_uris")
    except AttributeError as e:
        # Handle the AttributeError
        print("No printing of " + card_name + " found with id: " + id)
        formattedCardNames = []
        image_uris = []

    # Check if the image/images have already been downloaded
    for f_card_name in formattedCardNames:
        file_name = generateFileName(f_card_name, id)
        if os.path.exists(os.path.join(path, file_name)):
            print(generateFileName(f_card_name, id=id) +
                  " already downloaded! Using existing png")
            return printings

    # Open the url image, set stream to True, this will return the stream content.
    for image_uri, f_card_name in zip(image_uris, formattedCardNames):
        file_name = generateFileName(f_card_name, id)

        r = requests.get(image_uri, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            # Open a local file with wb ( write binary ) permission.
            with open(os.path.join(path, file_name), 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            print('Image successfully Downloaded: ', file_name)
        else:
            print('Image Couldn\'t be retrieved')
    return printings

# Retrieve all images for a dictionary of cards from scryfall's api


def GetAllImages(card_dict):
    all_card_printings = {}
    for card_name, card_quantity in card_dict.items():
        if card_quantity > 0:
            printing = GetCardImage(card_name)
            if printing.get("dual_faced") == "False":
                FormattedCardNames = [FormatCardName(card_name)]
            else:
                FormattedCardNames = splitCardName(card_name)

            for f_card_name in FormattedCardNames:
                all_card_printings[f_card_name] = printing
            t.sleep(0.05)
    return all_card_printings
