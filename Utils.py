# Fix bad file names
def FormatCardName(card_name):
    formattedCardName = card_name.replace("\"", "") # Replace slashes
    formattedCardName = card_name.replace("/", "") # Replace slashes
    formattedCardName = formattedCardName.replace(" ", "-") # Replace spaces 
    formattedCardName = formattedCardName.replace(",", "") # Delete commas
    formattedCardName = formattedCardName.replace("\"", "") # Delete quotes
    formattedCardName = formattedCardName.replace("\'", "") # Delete quotes
    formattedCardName = formattedCardName.lower()
    return formattedCardName

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