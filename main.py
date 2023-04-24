import FetchDecks as fd
import FetchImages as fi

def main():
    profile = "Hype"
    #fd.UpdateCurrentDecks(profile)
    #fi.GetCardImage("Burgeoning")
    #fi.GetDeckImages("Heads I Win Tails You Lose")
    #fd.SaveDecks()
    #fd.CompareDecks("Heads I Win Tails You Lose")
    fd.CompareAllDecks()
    
if __name__ == "__main__":
    main()
    