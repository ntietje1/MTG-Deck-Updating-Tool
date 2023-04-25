import FetchDecks as fd
import FetchImages as fi
import GeneratePDF as gp
import sys
import GUI as g

def main():
    # profile = "Hype"
    # fd.UpdateCurrentDecks(profile)
    # #fd.SaveDecks()
    # fd.CompareDecks("Henzie and Umori Companion.txt")
    # card_dict = fd.CompareAllDecks()
    # print("Full changes made: ")
    # print(card_dict)
    # fi.GetAllImages(card_dict)
    # gp.genPDF(card_dict)
    
    app = g.QApplication(sys.argv)

    # Create and show the main window
    window = g.MyWindow()
    window.show()

    # Run the event loop
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
    