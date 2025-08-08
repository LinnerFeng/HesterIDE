#Now we successfully downloaded the source code from github
import os
import sys
import subprocess
import zipfile
import shutil
import upload

def unzip_file(zip_path,extract_to):
    current_path=upload.get_path_for_downloaded_package(zip_path)
    if zipfile.is_zipfile(current_path):
        with zipfile.ZipFile(current_path,'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extracted {zip_path} to {extract_to}")
    else:
        raise zipfile.BadZipFile(f"{zip_path} is not a valid zip file.")

def run_launcher_files(launcher_files):
    if os.path.exists(launcher_files):
        if sys.platform.startswith('win'):
            subprocess.run([launcher_files], check=True)
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            subprocess.run(['chmod', '+x', launcher_files], check=True)
            subprocess.run([f'./{launcher_files}'], check=True)
        else:
            raise OSError("Unsupported OS type.")
    else:
        raise FileNotFoundError(f"Launcher file {launcher_files} does not exist.")
