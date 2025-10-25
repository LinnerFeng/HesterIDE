#this is using to select the GPU api
#it will select the best GPU api for the system
#win:Vulkan->DirectX->OpenGL
#linux:Vulkan->OpenGL
#mac:Metal->OpenGL
import platform
import os
import sys
import urllib.request
import zipfile

class APISelector:
    def __init__(self):
        self.api=None
    

    def select_and_download_api(self):
        system=platform.system()
        if system=="Windows":
            self.api="Vulkan"
        elif system=="Linux":
            self.api="Vulkan"
        elif system=="Darwin":
            self.api="Metal"
        else:
            self.api="OpenGL"
        self.download_api()

    def download_api(self):
        if self.api=="Vulkan":
            url="https://sdk.lunarg.com/sdk/download/latest/windows/VulkanSDK.exe"
        elif self.api=="Metal":
            url="https://developer.apple.com/metal/"
        else:
            url="https://www.opengl.org/"

        urllib.request.urlretrieve(url,"./"+self.api+".zip")
        with zipfile.ZipFile("./"+self.api+".zip","r") as zip_ref:
            zip_ref.extractall("./"+self.api)

if __name__=="__main__":
    selector=APISelector()
    selector.select_and_download_api()
    print(f"Selected and downloaded {selector.api} API")