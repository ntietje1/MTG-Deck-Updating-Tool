from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QPlainTextEdit, QMainWindow, QScrollArea, QLabel, QListWidgetItem
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QPaintEvent, QImage, QPixmap, QPalette, QBrush, QFont, QColor
from PySide6 import QtGui
from PySide6.QtWidgets import QProgressDialog

from PIL.ImageQt import ImageQt
from PIL import Image
import threading
import FetchDecks as fd
import FetchImages as fi
import GeneratePDF as gp

import os

class MyWindow(QMainWindow):
    card_dict = {}

    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("MTG Deck Updating Tool")

        # Create a central widget
        central_widget = QWidget(self)

        # Create a vertical layout for the central widget
        vbox = QVBoxLayout()

        # Create a horizontal layout for the top section (URL bar and button)
        url_box = QHBoxLayout()

        # Create the URL bar
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("Enter Moxfield profile URL or username here")
        self.url_bar.textChanged.connect(self.enable_disable_button)

        # Create a button for the URL bar
        self.url_button = QPushButton("Retrieve Decklists", self)
        self.url_button.clicked.connect(self.on_url_button_clicked)

        # Disable the button initially
        self.url_button.setEnabled(False)

        # Add the URL bar and button to the top section
        url_box.addWidget(self.url_bar)
        url_box.addWidget(self.url_button)

        # Add the top section to the vertical layout
        vbox.addLayout(url_box)

        # Create a horizontal layout for the buttons and the list widget
        hbox = QHBoxLayout()

        # Create a vertical layout for the list widget
        list_box = QVBoxLayout()

        # Create the list widget and image label widget
        self.list_widget = QListWidget(self)
        self.image_label = QLabel(self)

        # Add the list widget to the vertical layout
        list_box.addWidget(self.list_widget)
        list_box.addWidget(self.image_label)

        # Add the vertical layout to the horizontal layout
        hbox.addLayout(list_box)

        # Create a horizontal layout for the buttons
        vbox_buttons = QVBoxLayout()

        # Create the buttons
        self.button1 = QPushButton("Save Decks", self)
        self.button2 = QPushButton("Compare Decks", self)
        self.button3 = QPushButton("Choose Images", self)
        self.button4 = QPushButton("Generate PDF", self)

        # Connect each button to its corresponding function
        self.button1.clicked.connect(self.on_button1_clicked)
        self.button2.clicked.connect(self.on_button2_clicked)
        self.button3.clicked.connect(self.on_button3_clicked)
        self.button4.clicked.connect(self.on_button4_clicked)

        # Add the buttons to the vertical layout
        vbox_buttons.addWidget(self.button1)
        vbox_buttons.addWidget(self.button2)
        vbox_buttons.addWidget(self.button3)
        vbox_buttons.addWidget(self.button4)

        # Add the vertical layout to the horizontal layout
        hbox.addLayout(vbox_buttons)

        # Add the horizontal layout to the vertical layout
        vbox.addLayout(hbox)

        # Set the central widget
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)
        
        if fd.LastSavedDate != "no log file found!":
            # Set the list widget to display changes made to decks
            newItem = QListWidgetItem("Changes To Decks:")
            newFont = QFont()
            newFont.setPointSize(15)
            newFont.setBold(True)
            newItem.setFont(newFont)
            self.list_widget.addItem(newItem)
            newItem = QListWidgetItem("Decks last saved on: " + fd.LastSavedDate())
            newFont = QFont()
            newFont.setPointSize(10)
            newItem.setFont(newFont)
            self.list_widget.addItem(newItem)
        else:
            newItem = QListWidgetItem("Make a save of your decks before attempting to find changes!")

    def on_button1_clicked(self):
        print("Saving decks. . .")
        fd.SaveDecks()

    def on_button2_clicked(self):
        print("Checking for changes. . .")
        MyWindow.card_dict = fd.CompareAllDecks()
        
        for deck_title in os.listdir("Decks//"):
            if not deck_title.endswith('.txt'):
                continue
            
            diff_dict = fd.CompareDecks(deck_title)
            if (len(diff_dict) == 0):
                continue
            
            # Add the deck title to the list widget
            newItem = QListWidgetItem(deck_title + " Changes:")
            newItem.setBackground(QColor(253,253,255))
            newFont = QFont()
            newFont.setPointSize(11)
            newItem.setFont(newFont)
            self.list_widget.addItem(newItem)
            
            cardFont = QFont()
            cardFont.setItalic(True)
            for card_name, card_quantity in diff_dict.items():
                if card_quantity > 0: 
                    # Add an item to the list widget
                    newItem = QListWidgetItem("Added: " + card_name + " " + str(card_quantity) + "x")
                    newItem.setBackground(QColor(225, 250, 225))
                    newItem.setFont(cardFont)
                    self.list_widget.addItem(newItem)
            for card_name, card_quantity in diff_dict.items():
                if card_quantity < 0:
                    # Add an item to the list widget
                    newItem = QListWidgetItem("Removed: " + card_name + " " + str(card_quantity) + "x")
                    newItem.setBackground(QColor(250, 225, 225))
                    newItem.setFont(cardFont)
                    self.list_widget.addItem(newItem)
            #self.list_widget.addItem("")
            
    def on_button3_clicked(self):
        # Switch between list widget and image viewing area
        if self.list_widget.isVisible():
            # Show image viewing area
            self.list_widget.setVisible(False)
            self.image_label.setVisible(True)
            self.button3.setText('Switch to List View')

            # Load image from file and set as image label pixmap
            pixmap = QPixmap()
            image_path = os.getcwd() + "\\Images\\Island.png"
            image = Image.open(image_path)
            qimage = ImageQt(image)
            pixmap = QtGui.QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)
        else:
            # Show list widget
            self.image_label.setVisible(False)
            self.list_widget.setVisible(True)
            self.button3.setText('Switch to Image View')
    
    def on_button4_clicked(self):
        print("Generating pdf. . .")

        # Call the GetAllImages and genPDF functions in separate threads to avoid freezing the GUI
        thread1 = threading.Thread(target=fi.GetAllImages, args=(MyWindow.card_dict,))
        thread1.start()
        
        thread2 = threading.Thread(target=gp.genPDF, args=(MyWindow.card_dict,))
        thread2.start()
    
    def on_url_button_clicked(self):
        text = self.url_bar.text()
        if len(text) != 0:
            print(f"Retrieving decks from {text}...")

            # Call the UpdateCurrentDecks function in a separate thread to avoid freezing the GUI
            thread = threading.Thread(target=fd.UpdateCurrentDecks, args=(text,))
            thread.start()
        
    def enable_disable_button(self):
        # Enable/disable the button based on whether the text box is empty or not
        if self.url_bar.text():
            self.url_button.setEnabled(True)
        else:
            self.url_button.setEnabled(False)