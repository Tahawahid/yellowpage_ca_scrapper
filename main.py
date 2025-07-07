"""Main entry point for Yellow Pages Scraper Application"""

import tkinter as tk
from gui_app import YellowPagesApp


def main():
    """Main function to start the application"""
    root = tk.Tk()
    app = YellowPagesApp(root)
    
    # Center the window on the screen
    root.eval('tk::PlaceWindow . center')
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()