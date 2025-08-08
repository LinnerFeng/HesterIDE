import subprocess
import os
import sys

#The launch is to redigst the package's main file into a process

def launch():
    """Launch the main file of the package."""
    current_directory = os.getcwd()
    main_file = os.path.join(current_directory, 'main.py')  # Assuming main.py is the entry point
    if os.path.exists(main_file):
        if sys.platform.startswith('win'):
            subprocess.run(['python', main_file], check=True)
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            subprocess.run(['python3', main_file], check=True)
        else:
            raise OSError("Unsupported OS type.")
    else:
        raise FileNotFoundError(f"Main file {main_file} does not exist.")