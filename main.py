import FetchDecks as fd
import FetchImages as fi

def main():
    profile = "Hype"
    #fd.UpdateCurrentDecks(profile)
    #fi.GetCardImage("Burgeoning")
    fi.GetDeckImages("Heads I Win Tails You Lose")
    
    
if __name__ == "__main__":
    main()
    