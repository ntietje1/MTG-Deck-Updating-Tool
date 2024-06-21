import os
import fitz
import FetchImages as fi
from datetime import datetime

# Returns the path of a generated pdf if one were to be generated


def getPDFPath():
    return os.getcwd() + "\\PDFs\\deck-" + datetime.now().strftime("%d-%m-%Y") + ".pdf"

# Generate a pdf with card images true to size
# Saves the pdf to the /PDFs directory


def genPDF(final_printing_selections):
    card_width = 2.5  # inches
    card_height = 3.5  # inches
    pixel_width = 745  # pixels
    pixel_height = 1040  # pixels
    resolution = pixel_width/card_width  # pixels per inch (about 300)
    cards_per_row = 3
    cards_per_col = 3
    cards_per_page = cards_per_row * cards_per_col
    page_width_pixels = 8.5*resolution
    page_height_pixels = 11*resolution

    # Calculate the border size in order to center cards
    row_border_size = (page_width_pixels - cards_per_row * pixel_width)/2
    col_border_size = (page_height_pixels - cards_per_row * pixel_height)/2

    # # Convert cards hashmap into a list of cards to print
    # num_cards_added = 0
    # added_cards = [] # create a list of added cards (multiple cards added as duplicates)
    # for card_name, card_quantity in card_dict.items():
    #     if card_quantity > 0:
    #         for i in range(card_quantity):
    #             added_cards.append(card_name)
    #             num_cards_added = num_cards_added + card_quantity
    # else:
    #     for i in range(-1 * card_quantity):
    #         removed_cards_dict[card_name] = -1 * card_quantity

    # Prevent attempting to output a 0 page pdf
    if len(final_printing_selections) == 0:
        print("No images selected! No PDF generated :(")
        return

    # Create the PDFs directory if it doesn't exist
    pdfs_dir = os.getcwd() + "\\PDFs"
    os.makedirs(pdfs_dir, exist_ok=True)

    # Create a blank pdf
    pdf_path = os.getcwd() + "\\PDFs\\deck-" + \
        datetime.now().strftime("%m-%d-%Y") + ".pdf"
    deck_pdf = fitz.open()

    # Loop over each card image and add it to the blank pdf
    j = 0
    for card_name, id in final_printing_selections.items():
        if (j % cards_per_page == 0):
            page = deck_pdf.new_page(
                width=page_width_pixels, height=page_height_pixels)
            j = 0

        img_path = os.getcwd() + "\\Images\\" + fi.generateFileName(card_name, id)

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
        image_coords = fitz.Rect(x1, y1, x2, y2)
        page.show_pdf_page(image_coords, card_pdf, 0)

        j = j + 1

    # Save the generated pdf
    deck_pdf.save(pdf_path)
