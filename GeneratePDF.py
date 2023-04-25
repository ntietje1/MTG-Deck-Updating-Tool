import os
import fitz
import Utils as u
from datetime import datetime

# Generate a pdf with card images true to size
# Saves the pdf to the /PDFs directory
def genPDF(card_dict):
    card_width = 2.5 # inches
    card_height = 3.5 # inches
    pixel_width = 745 # pixels
    pixel_height = 1040 # pixels
    resolution = pixel_width/card_width # pixels per inch (about 300)
    cards_per_row = 3
    cards_per_col = 3
    cards_per_page = cards_per_row * cards_per_col 
    page_width_pixels =8.5*resolution
    page_height_pixels =11*resolution
    
    # Calculate the border size in order to center cards
    row_border_size = (page_width_pixels - cards_per_row * pixel_width)/2
    col_border_size = (page_height_pixels - cards_per_row * pixel_height)/2
    
    # Convert cards hashmap into a list of cards to print
    num_cards_added = 0
    added_cards = []
    removed_cards_dict = {}
    for card_name, card_quantity in card_dict.items():
        if card_quantity > 0:
            for i in range(card_quantity):
                added_cards.append(card_name)
                num_cards_added = num_cards_added + card_quantity
        else:
            for i in range(-1 * card_quantity):
                removed_cards_dict[card_name] = -1 * card_quantity
                
    # Prevent attempting to output a 0 page pdf
    if num_cards_added == 0:
        print("No deck additions found! No PDF generated :(")
        return
    
    # Create a blank pdf
    pdf_path = os.getcwd() + "\\PDFs\\deck-" + datetime.now().strftime("%d-%m-%Y") + ".pdf"
    deck_pdf = fitz.open()

    # Loop over each card image and add it to the blank pdf
    j = 0
    for card_name in added_cards:
        if (j % cards_per_page == 0):
            page = deck_pdf.new_page(width = page_width_pixels, height = page_height_pixels)
            j = 0
        
        # Convert png file to pdf
        formattedCardName = u.FormatCardName(card_name)
        img_path = os.getcwd() + "\\Images\\" + formattedCardName + ".png"
        # Check if the image has been downloaded
        if not os.path.exists(img_path):
            print("Found card whose image is not downloaded, attempting to split")
            # Try splitting the card name (for dual faced cards)
            split_index = formattedCardName.find("--")
            # If the card is dual faced, fix card name to that of the front face and add back face to list of cards to be added
            if split_index != -1 and os.path.exists(os.getcwd() + "\\Images\\" + formattedCardName[:split_index] + ".png"):
                print("split successful!" + formattedCardName[:split_index] + " " + formattedCardName[split_index+2:])
                added_cards.append(formattedCardName[split_index+2:])
                formattedCardName = formattedCardName[:split_index]
                img_path = os.getcwd() + "\\Images\\" + formattedCardName + ".png"
            else:
                return
        # Convert the png to pdf
        card_image = fitz.open(img_path)
        pdfbytes = card_image.convert_to_pdf()
        card_image.close()
        card_pdf = fitz.open("pdf", pdfbytes)

        # Calculate the position of the card on the canvas
        row = j // cards_per_row
        col = j % cards_per_row
        x1 = col*pixel_width+row_border_size
        y1 = row*pixel_height+col_border_size
        x2 = (col+1)*pixel_width+row_border_size
        y2 = (row+1)*pixel_height+col_border_size

        # Add the card to the output PDF
        image_coords = fitz.Rect(x1,y1,x2,y2)
        page.show_pdf_page(image_coords, card_pdf, 0)
        
        j = j + 1
    
    # Save the generated pdf    
    deck_pdf.save(pdf_path)
    for card_name, card_quantity in removed_cards_dict.items():
        print("REMOVE: " + card_name + " " + str(card_quantity) + "x")
        
        

