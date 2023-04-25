import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QStatusBar, QToolBar, QFileDialog, QGridLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QCoreApplication, QObject, QRunnable, QThreadPool, Signal, QThread
import FetchDecks as fd
import FetchImages as fi
import GeneratePDF as gp

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
        hbox_top = QHBoxLayout()

        # Create the URL bar
        self.url_bar = QLineEdit(self)

        # Create a button for the URL bar
        self.url_button = QPushButton("Retrieve Decklists", self)
        self.url_button.clicked.connect(self.on_url_button_clicked)
        
        # Disable the button initially
        self.url_button.setEnabled(False)

        # Add the URL bar and button to the top section
        hbox_top.addWidget(self.url_bar)
        hbox_top.addWidget(self.url_button)

        # Add the top section to the vertical layout
        vbox.addLayout(hbox_top)

        # Create a horizontal layout for the buttons
        hbox_buttons = QHBoxLayout()

        # Create the buttons
        button1 = QPushButton("Save Decks", self)
        button2 = QPushButton("Compare Decks", self)
        button3 = QPushButton("Generate PDF", self)

        # Connect each button to its corresponding function
        button1.clicked.connect(self.on_button1_clicked)
        button2.clicked.connect(self.on_button2_clicked)
        button3.clicked.connect(self.on_button3_clicked)

        # Add the buttons to the horizontal layout
        hbox_buttons.addWidget(button1)
        hbox_buttons.addWidget(button2)
        hbox_buttons.addWidget(button3)

        # Add the buttons to the vertical layout
        vbox.addLayout(hbox_buttons)

        # Set the central widget
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)
        
        # Connect the text box to the method that enables/disables the button
        self.url_bar.textChanged.connect(self.enable_disable_button)

    def on_button1_clicked(self):
        print("Saving decks. . .")
        fd.SaveDecks()

    def on_button2_clicked(self):
        print("Checking for changes. . .")
        MyWindow.card_dict = fd.CompareAllDecks()

    def on_button3_clicked(self):
        print("Generating pdf. . .")
        fi.GetAllImages(MyWindow.card_dict)
        gp.genPDF(MyWindow.card_dict)

    def on_url_button_clicked(self):
        text = self.url_bar.text()
        if len(text) != 0:
            print(f"Retrieving decks from {text} . . .")
            fd.UpdateCurrentDecks(text)
            
    def enable_disable_button(self):
        # Enable/disable the button based on whether the text box is empty or not
        if self.url_bar.text():
            self.url_button.setEnabled(True)
        else:
            self.url_button.setEnabled(False)