from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from PIL.ImageQt import ImageQt
from PIL import Image
import threading
import FetchDecks as fd
import FetchImages as fi
import GeneratePDF as gp

import os


class MyQComboBox(QComboBox):
    def __init__(self, mtg_tool, scrollWidget=None, *args, **kwargs):
        super(MyQComboBox, self).__init__(*args, **kwargs)  
        self.scrollWidget = scrollWidget
        self.mtg_tool = mtg_tool
        self.setFocusPolicy(Qt.StrongFocus)
        self.currentIndexChanged.connect(self.on_combo_box_changed)
        self.user_interacted = False

    def wheelEvent(self, event):
        if self.hasFocus():
            return super().wheelEvent(event)
        else:
            return self.scrollWidget.wheelEvent(event)
    
    def on_combo_box_changed(self):
        if not self.user_interacted:  # check if the flag is False
            self.user_interacted = True  # set the flag to True
            return  # skip the function call
        
        text = self.currentText()
        set_code = self.mtg_tool.set_mapping.get(text)
        name = self.objectName()
        print("Selected:", set_code, "from", name)
        self.mtg_tool.insert_image(name, set_code)



class MTGDeckUpdatingTool(QMainWindow):
    card_dict = {}
    image_mapping = {}
    set_mapping = {}
    
    def __init__(self):
        super().__init__()
            
        # Create a central widget
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")

        # Create a vertical layout for the central widget
        self.central_vbox = QVBoxLayout()
        self.central_vbox.setObjectName("central_vbox")

        # Set the central widget
        self.central_widget.setLayout(self.central_vbox)
        self.setCentralWidget(self.central_widget)
        
        # Create a grid layout 
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        
        # Create a vertical layout to hold the url_box and main area
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout_2")
        
        # Create a horizontal layout for the URL box and button
        self.url_box = QHBoxLayout()
        self.url_box.setObjectName(u"url_box")
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("Enter Moxfield profile URL or username here")
        self.url_bar.textChanged.connect(self.enable_disable_button)
        
        # Create a line edit for the URL
        self.url_bar.setObjectName(u"url_bar")
        self.url_box.addWidget(self.url_bar)
        
        # Create a button for fetching the deck list
        self.url_button = QPushButton(self)
        self.url_button.setObjectName(u"url_button")
        self.url_button.clicked.connect(self.on_url_button_clicked)
        self.url_button.setEnabled(False) # Disable the button initially
        self.url_box.addWidget(self.url_button)
        
        # Add the URL box and button to the vertical layout
        self.verticalLayout.addLayout(self.url_box)

        # Create a horizontal layout for the tab widget and the buttons
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout_4")
        
        # Create a tab widget for the deck list and deck editor tabs
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(2)
        sizePolicy1.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy1)
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tab_2.sizePolicy().hasHeightForWidth())
        self.tab_2.setSizePolicy(sizePolicy2)

        # Add the list widget to a vbox that is inside the tab
        list_vbox= QVBoxLayout(self.tab_2)
        self.list_widget = QListWidget(self.tab_2)
        self.list_widget.setObjectName(u"list_widget")
        list_vbox.addWidget(self.list_widget)
        self.tab_2.setLayout(list_vbox)
        self.tabWidget.addTab(self.tab_2, "")
        
        self.add_list_header()
        
        # Add another tab
        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        
        # Add the image viewing grid layout
        self.grid_vbox = QVBoxLayout(self.tab)
        self.grid_vbox.setObjectName(u"grid_vbox")
        self.grid_vbox.setContentsMargins(0,0,0,0)

        # create a widget to hold the scroll area and set its minimum width to 580
        scroll_area_widget = QWidget()
        scroll_area_widget.setMinimumWidth(600)
        scroll_area_widget.setMinimumHeight(300)
        scroll_area_widget.setContentsMargins(0,0,0,0)

        self.scrollArea = QScrollArea(scroll_area_widget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True) # allow contents to be resized
        self.scrollArea.setMinimumWidth(610)
        self.scrollArea.setMinimumHeight(360)
        self.scrollArea.setContentsMargins(0,0,0,0)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setContentsMargins(0,0,0,0)

        # create a layout for the contents widget
        self.gridLayout_5 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(10,10,10,10)

        # set the contents widget as the scroll area widget
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        # add the scroll area to the scroll area widget
        layout = QVBoxLayout(scroll_area_widget)
        layout.addWidget(self.scrollArea)

        # add the scroll area widget to the main layout
        self.grid_vbox.addWidget(scroll_area_widget)
        self.tabWidget.addTab(self.tab, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        
        # Create vert layout to hold buttons
        self.button_layout = QVBoxLayout()
        self.button_layout.setObjectName(u"button_layout")
        
        # Create four buttons
        self.button_1 = QPushButton(self)
        self.button_1.setObjectName(u"button_1")
        self.button_layout.addWidget(self.button_1)
        self.button_1.clicked.connect(self.on_button1_clicked)
        
        self.button_2 = QPushButton(self)
        self.button_2.setObjectName(u"button_2")
        self.button_layout.addWidget(self.button_2)
        self.button_2.clicked.connect(self.on_button2_clicked)
        
        self.button_3 = QPushButton(self)
        self.button_3.setObjectName(u"button_3")
        self.button_layout.addWidget(self.button_3)
        self.button_3.clicked.connect(self.on_button3_clicked)
        
        self.button_4 = QPushButton(self)
        self.button_4.setObjectName(u"button_4")
        self.button_layout.addWidget(self.button_4)
        self.button_4.clicked.connect(self.on_button4_clicked)

        # Add the button layout to the gui
        self.horizontalLayout.addLayout(self.button_layout)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(1, 1)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        
        # Add the widgets and layouts to the vertical layout
        self.central_vbox.addLayout(self.gridLayout)

        self.retranslateUi(self)

        self.tabWidget.setCurrentIndex(0)
    
    # Add translation capability    
    def retranslateUi(self, MTGDeckUpdatingTool):
        MTGDeckUpdatingTool.setWindowTitle(QCoreApplication.translate("MTGDeckUpdatingTool", u"Dialog", None))
        self.url_button.setText(QCoreApplication.translate("MTGDeckUpdatingTool", u"Retrieve Decks", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MTGDeckUpdatingTool", u"Deck Changes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MTGDeckUpdatingTool", u"Images", None))
        self.button_1.setText(QCoreApplication.translate("MTGDeckUpdatingTool", u"Save Decks", None))
        self.button_2.setText(QCoreApplication.translate("MTGDeckUpdatingTool", u"Find Changes", None))
        self.button_3.setText(QCoreApplication.translate("MTGDeckUpdatingTool", u"Manual Mode", None))
        self.button_4.setText(QCoreApplication.translate("MTGDeckUpdatingTool", u"Generate PDF", None))
    
    # Add two items to the top of the list widget as a header    
    def add_list_header(self):
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
            self.list_widget.addItem(newItem)
    
    # Populate list widget with current deck changes        
    def update_list_widget(self):
        self.list_widget.clear()
        self.add_list_header()
        MTGDeckUpdatingTool.card_dict = fd.CompareAllDecks()
        
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
                    
    def init_images_widget(self):
        all_card_printings = {}
        all_card_printings = fi.GetAllImages(self.card_dict)
        print(all_card_printings)

        added_cards = [] # create a list of added cards
        for card_name, card_quantity in self.card_dict.items():
            if card_quantity > 0:
                print("Getting printings for: " + card_name)
                printings = fi.getPrintings(card_name)
                FormattedCardName = fi.FormatCardName(card_name)
                print("attempting to add images for: " + FormattedCardName)
                # added_cards.extend(printings.get("def").get("formattedCardNames"))
                default_set_code = next(iter(printings))
                added_cards.extend(printings.get(default_set_code).get("formattedCardNames"))

        cards_per_row = 3
        for i, f_card_name in enumerate(added_cards):
            image_path = os.getcwd() + "\\Images\\" + f_card_name + "-def" + ".png"
            row = i // cards_per_row
            col = i % cards_per_row

            image = Image.open(image_path)

            qimage = ImageQt(image)
            pixmap = QPixmap.fromImage(qimage)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setScaledContents(True)
            image_label.setFixedSize(560//3, 560//3//2.5*3.5)

            vlayout = QVBoxLayout()
            vlayout.addWidget(image_label)
            vlayout.setAlignment(Qt.AlignCenter)

            combo_box = MyQComboBox(self, scrollWidget=self.scrollArea)
            combo_box.setObjectName(f_card_name)
            print("Adding dropdown items to: " + f_card_name)
            printings = fi.getPrintings(f_card_name)
            for set, printing in printings.items():
                print("Adding set to " + f_card_name + "dropdown: " + str(set))
                combo_box.addItems([printing.get("set_name")])
                self.set_mapping[printing.get("set_name")] =  printing.get("set_code")
            combo_box.setFixedWidth(image_label.width()) # Set the width of the dropdown to match the width of the image
            
            hlayout = QHBoxLayout()
            hlayout.addWidget(combo_box)
            vlayout.addLayout(hlayout)

            print("Added " + f_card_name + " to image layout at position: (" + str(row) + ", " + str(col) + ")")
            self.gridLayout_5.addLayout(vlayout, row, col, 1, 1)
            self.image_mapping[f_card_name] = tuple((row, col))
            print("Added " + f_card_name + " to image_mapping")
            print("new image mapping: ")
            print(self.image_mapping)
        
    def insert_image(self, f_card_name, set):
        fi.GetCardImage(f_card_name, set_code = set)
        print("image mapping:")
        print("Retrieving coordinates for: " + f_card_name)
        print(self.image_mapping.get(f_card_name)) # why none??
        coordinate = self.image_mapping.get(f_card_name)
        print(type(coordinate))
        print(coordinate)
        row = coordinate[0]
        col = coordinate[1]
        
        image_path = os.getcwd() + "\\Images\\" + f_card_name + "-" + set + ".png"

        image = Image.open(image_path)

        qimage = ImageQt(image)
        pixmap = QPixmap.fromImage(qimage)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)
        image_label.setFixedSize(560//3, 560//3//2.5*3.5)

        vlayout = QVBoxLayout()
        vlayout.addWidget(image_label)
        vlayout.setAlignment(Qt.AlignCenter)

        combo_box = self.retrieve_combo_box(row, col)
        hlayout = QHBoxLayout()
        hlayout.addWidget(combo_box)
        vlayout.addLayout(hlayout)

        print("Added " + f_card_name + " to image layout at position: (" + str(row) + ", " + str(col) + ")")
        self.remove_item_at_position(row, col)
        self.gridLayout_5.addLayout(vlayout, row, col, 1, 1)
        
        return
    
    def retrieve_combo_box(self,row,col):
        previous_vlayout = self.gridLayout_5.itemAtPosition(row, col)
        if previous_vlayout is not None:
            previous_hlayout = previous_vlayout.itemAt(1) # Get the QHBoxLayout containing the previous widget
            previous_combo_box = previous_hlayout.itemAt(0).widget() # Get the QComboBox widget from the QHBoxLayout
            return previous_combo_box
                
    
    def remove_item_at_position(self, row, col):
        item = self.gridLayout_5.itemAtPosition(row, col)
        if item is not None:
            widget = item.widget()
            if widget is not None:
                self.gridLayout_5.removeWidget(widget)
                widget.deleteLater()
            else:
                self.gridLayout_5.removeItem(item)
        
    
    # Run the save decks function on
    def on_button1_clicked(self):
        print("Saving decks. . .")
        fd.SaveDecks()

    def on_button2_clicked(self):
        
        print("Checking for changes. . .")
        self.update_list_widget()
        self.init_images_widget()
            
    def on_button3_clicked(self):
        print("button 3 clicked!")
    
    def on_button4_clicked(self):
        print("Generating pdf. . .")

        # Call the GetAllImages and genPDF functions in separate threads to avoid freezing the GUI
        thread1 = threading.Thread(target=fi.GetAllImages, args=(MTGDeckUpdatingTool.card_dict,))
        thread1.start()
        thread1.join()
        
        thread2 = threading.Thread(target=gp.genPDF, args=(MTGDeckUpdatingTool.card_dict,))
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
        