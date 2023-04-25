import FetchDecks as fd
import FetchImages as fi
import GeneratePDF as gp

def main():
    profile = "Hype"
    #fd.UpdateCurrentDecks(profile)
    #fi.GetCardImage("Burgeoning")
    #fi.GetDeckImages("Henzie and Umori Companion")
    #fd.SaveDecks()
    #fd.CompareDecks("Henzie and Umori Companion.txt")
    #fi.GetAllImages()
    card_dict = fd.CompareAllDecks()
    print("Full changes made: ")
    print(card_dict)
    gp.genPDF(card_dict)
    
    
if __name__ == "__main__":
    main()
    