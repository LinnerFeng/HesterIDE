#for extern package ,we can use this file to upload file on the GitHub
import os
import sys
import subprocess
import requests

BACKUP_URLs={
    "Backup1":"https://hub.fastgit.org/", 
    "Backup2":"https://ghproxy.com/https://github.com/",
    "Buckup3":"https://gitclone.com/github.com/",
    #--------------------------------------
    #Now These Backuup URLs are for some places that block github
    #Like some country in Asia and Europe
    #also have north America
    #--------------------------------------
    "Backup4":"https://us.github.91chi.fun/https://github.com",#North America
    "Backup5":"https://ca.gitclone.com/github.com/",#Canada
    "Backup6":"https://uk.gitclone.com/github.com/",#United Kingdom
    "Backup7":"https://de.gitclone.com/github.com/",#Germany
    "Backup8":"https://fr.gitclone.com/github.com/",#France
    "Backup9":"https://es.gitclone.com/github.com/",#Spain
    "Backup10":"https://it.gitclone.com/github.com/",#Italy
    "Backup11":"https://in.gitclone.com/github.com/",#India
    "Backup12":"https://jp.gitclone.com/github.com/",#Japan
    "Backup13":"https://kr.gitclone.com/github.com/",#Korea
    "Backup14":"https://au.gitclone.com/github.com/",#Australia
    "Backup15":"https://sg.gitclone.com/github.com/",#Singapore
    "Backup16":"https://hk.gitclone.com/github.com/",#HongKong
    "Backup17":"https://tw.gitclone.com/github.com/",#Taiwan
    "Backup18":"https://cn.gitclone.com/github.com/",#China
    #------------------------------------------------------
    #... You can add more backup URLs if you want
    #------------------------------------------------------
    "Backup_":"https://gitlab.com/api/v4/projects/278964/repository/files/%2Fblob%2Fmaster%2FREADME.md/raw?ref=master",
}

def get_source_code(url):
    """Get your package's source code from your repository."""
    repo_url = url
    try:
        #because we're already in the repoand install git
        subprocess.run(["git", "clone", repo_url], check=True)
        print("Source code downloaded successfully.")
    except subprocess.CalledProcessError as e:
        #Now fix it with backup URLs
        print(f"Failed to clone repository: {e}")
        print("Trying backup URLs...")
        try:
            for backup_name, backup_url in BACKUP_URLs.items():
                print(f"Trying {backup_name}...")
                subprocess.run(["git", "clone", backup_url], check=True)
                print("Source code downloaded successfully from backup.")
                return
        except subprocess.CalledProcessError as e:
            print("All backup URLs failed.")
            sys.exit(1)
            raise OSError("Failed to download source code from all URLs.")
def get_extern_package_info(users_input):
    """Get users input and search it in all github repository"""
    search_url = f"https://api.github.com/search/repositories?q={users_input}+in:name,description"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if not items:
            print("No repositories found.")
            return None
        print("Found repositories:")
        for idx, item in enumerate(items, start=1):
            print(f"{idx}. {item['full_name']}: {item['html_url']}")
        choice = int(input("Enter the number of the repository to clone (0 to cancel): "))
        if choice == 0:
            print("Operation cancelled.")
            return None
        selected_repo = items[choice - 1]
        return selected_repo['html_url']
    except requests.RequestException as e:
        print(f"Error fetching repository data: {e}")
        return None
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

def get_path_for_downloaded_package(package_name):
    """Get the path of the downloaded package."""
    current_dictory=os.getcwd()
    package_path=os.path.join(current_dictory,package_name)
    if os.path.exists(package_path):
        return package_path
    else:
        raise FileNotFoundError(f"Package path {package_path} does not exist.")

def main():
    """Main function to handle the process."""
    users_input = input("Enter the name of the package you want to download: ")
    repo_url = get_extern_package_info(users_input)
    if repo_url:
        get_source_code(repo_url)
        package_path = get_path_for_downloaded_package(users_input)
        print(f"Package downloaded to: {package_path}")
    else:
        print("No valid repository URL provided.")