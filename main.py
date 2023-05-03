import sys
import GUI as g
import FetchImages as fi
import FetchDecks as fd

def main():
    # fi.getPrintings("Etali, Primal Conqueror // Etali, Primal Sickness")
    # fi.getPrintings("Burgeoning")
    
    # card_dict = fd.CompareAllDecks()
    # all_card_printings = fi.GetAllImages(card_dict)
    # print("--------------------------------------------------------------------")
    # print(all_card_printings)
    
    # fi.GetCardImage("Burgeoning", set_code = "SLD")
    # fi.GetCardImage("Burgeoning")
    
    app = g.QApplication(sys.argv)

    # Create and show the main window
    window = g.MTGDeckUpdatingTool()
    window.show()

    # Run the event loop
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
    