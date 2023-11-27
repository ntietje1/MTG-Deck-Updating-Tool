# MTG Deck Updating Tool

The MTG Deck Updating Tool simplifies the process of managing and updating multiple decks hosted on moxfield.com while offering features for proxying changes and customizing print-ready PDFs.

## Features

- **Version Tracking:** Keep a history of changes for publicly listed decks associated with a moxfield profile.
- **Change Analysis:** Generate lists of card additions/deletions and print-ready PDFs for easy proxying of changes in various paper dimensions.
- **Card Proxying:** Choose from all printings of a card to create proxies. Includes a manual mode for direct card name entry.
  
## Technologies Used

- **PySide6:** For GUI handling using XML-based layouts.
- **fitz:** For PDF creation and modification.
- **Selenium:** Web-scraping for moxfield profile data.


## Installation

To run the tool, simply download the project files and execute `main.py`.

## Usage Instructions

1. Enter your moxfield profile link in the URL bar to create a save of your publicly listed decks.
2. After making changes, create a new save to visualize the modifications made.

## Future Development

- **Porting to JavaScript:** Consideration to port some or all of the tool to JavaScript + a cloud-based storage solution for web and mobile usage.
- **Additional Website Support:** Support for alternative deck-hosting websites may be added in the future.
  
## Contributing

While direct contributions are not accepted at this time, suggestions for improvements or features are highly appreciated.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
