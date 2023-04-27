import sys
import GUI as g

def main():
    app = g.QApplication(sys.argv)

    # Create and show the main window
    window = g.MyWindow()
    window.show()

    # Run the event loop
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
    