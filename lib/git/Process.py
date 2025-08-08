import os
import subprocess
import sys
import zipfile
import shutil

import urllib.request

COUNTRYS={"China":"https://mirrors.tuna.tsinghua.edu.cn/git/git-for-windows/git-2.41.0-64-bit.7z.exe",
            "USA":"https://https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.1/PortableGit-2.41.0-64-bit.7z.exe",
            "India":"https://mirrors.edge.kernel.org/pub/software/scm/git/git-2.41.0.tar.gz",
            "Germany":"https://mirrors.edge.kernel.org/pub/software/scm/git/git-2.41.0.tar.gz",
            "Backup":"https://download.fastgit.org/git-for-windows/git/releases/download/v2.41.0.windows.1/PortableGit-2.41.0-64-bit.7z.exe"
            }

def is_git_installed():
    """Check if Git is installed on the system."""
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

def download_and_install_git_in_windows():
    """Download and install Git binary release."""
    print("Git is not installed. Downloading Git...")
    git_url = "https://github.com/git-for-windows/git/releases/latest/download/PortableGit-2.41.0-64-bit.7z.exe"  # Update URL if needed
    download_path = "git_installer.exe"

    try:
        urllib.request.urlretrieve(git_url, download_path)
        print("Git downloaded successfully. Installing...")

        # Run the installer silently
        subprocess.run([download_path, '/VERYSILENT', '/NORESTART'], check=True)
        print("Git installed successfully.")
    except Exception as e:
        print(f"Failed to download or install Git: {e}")
        #Try the mirror address
        backup_url_1 = "https://mirrors.edge.kernel.org/pub/software/scm/git/git-2.41.0.tar.gz"
        try:
            urllib.request.urlretrieve(backup_url_1, download_path)
            print(f"Git downloaded successfully from mirror {backup_url_1}. Installing...")
            subprocess.run([download_path, '/VERYSILENT', '/NORESTART'], check=True)
            print("Git installed successfully.")
        except Exception as e:
            print(f"Failed to download or install Git from mirror: {e}")
            sys.exit(1)
            #If you still download failed I will ask your country and find mirror path for quick one
            country = input("Please enter your country (China, USA, India, Germany) or type 'Backup' for backup link: ")
            if country  in COUNTRYS:
                url_new=COUNTRYS[country]
            else:
                url_new=COUNTRYS["Backup"]
                try:
                    urllib.request.urlretrieve(url_new, download_path)
                    print(f"Git downloaded successfully from mirror {url_new}. Installing...")
                    subprocess.run([download_path, '/VERYSILENT', '/NORESTART'], check=True)
                    print("Git installed successfully.")
                except Exception as e:
                    print(f"Failed to download or install Git from mirror: {e}")
                    sys.exit(1)

    finally:
        if os.path.exists(download_path):
            os.remove(download_path)

def download_and_install_git_in_linux():
    """Install Git using the package manager."""
    try:
        subprocess.run(["sudo","apt-get","update"],check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "git"], check=True)
        print("Git installed successfully.")
    except subprocess.CalledProcessError as e:
        try:
            subprocess.run(["sudo","yum","install","git","-y"],check=True)#This is for CentOS 7 and RHEL 7
            print("Git installed successfully.")
        except subprocess.CalledProcessError as e:
            try:
                subprocess.run(["sudo","dnf","install","git","-y"],check=True)#This is for CentOS 8 and RHEL 8
                print("Git installed successfully.")
            except subprocess.CalledProcessError as e:
                try:
                    subprocess.run(["sudo","pacman","-S","git","--noconfirm"],check=True)#This is for Arch Linux
                    print("Git installed successfully.")
                except subprocess.CalledProcessError as e:
                    try:
                        subprocess.run(["sudo","zypper","install","git","-y"],check=True)#This is for openSUSE
                        print("Git installed successfully.")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to install Git: {e}")
                        sys.exit(1)
                        raise OSError("Unknow OS type try to install git manually")
            
def download_git_and_install_git_int_mac():
    """Install git in MacOS with multiple way"""
    try:
        subprocess.run(["brew","install","git"],check=True)#if you install homebrew
        print("Git installed successfully.")
    except subprocess.CalledProcessError as e:
        #if you don't install any package manager
        subprocess.run([f"/bin/bash","-c","-$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"],check=True)
        subprocess.run(["brew","install","git"],check=True)
        try:
            subprocess.run(["git","--version"],check=True)#check git is working on your computer and print the version
        except subprocess.CalledProcessError as e:
            try:
                subprocess.run(["curl","-LO","https://sourceforge.net/projects/git-osx-installer/files/latest/download"],check=True)
                subprocess.run(["sudo","installer","-pkg","download","-target","/"],check=True)
            except subprocess.CalledProcessError as e:
                try:
                    subprocess.run(["xcode-select","--install"],check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install Git: {e}")
                    sys.exit(1)
                    raise OSError("Unknow OS type try to install git manually")
        print("Git installed successfully.")

def git_commit_and_push(commit_message):
    """Commit and push changes using Git."""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Changes committed and pushed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        sys.exit(1)

def git_check_system_info():
    """
    To check of your system and install it

    Because of many system have different way to install git
    """
    if sys.platform.startswith('win'):
        return "Windows"
    elif sys.platform.startswith('linux'):
        return "Linux"
    elif sys.platform.startswith('darwin'):
        return "MacOS"
    else:
        raise OSError("Unknow OS type try to install git manually")

if __name__ == "__main__":
    if not is_git_installed() and git_check_system_info() == "Windows":
        download_and_install_git_in_windows()
    elif not is_git_installed() and git_check_system_info() == "Linux":
        download_and_install_git_in_linux()
    elif not is_git_installed() and git_check_system_info() == "MacOS":
        download_git_and_install_git_int_mac()
    else:
        print("Git is already installed.")
        input("Do you want to commit and push changes? (Press Enter to continue)")
        commit_message = input("Enter commit message: ")
        git_commit_and_push(commit_message)