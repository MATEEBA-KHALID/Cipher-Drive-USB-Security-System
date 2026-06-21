# run_gui.py
#!/usr/bin/env python3
"""
Cipher Drive GUI Launcher
Run this file to start the GUI application
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui_main import main
    
    if __name__ == "__main__":
        print(" Starting Cipher Drive GUI...")
        main()
        
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("pip install tkinter pycryptodome psutil watchdog cryptography python-dotenv colorama")
    input("\nPress Enter to exit...")