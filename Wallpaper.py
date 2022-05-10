# Wallpaper.get() Get current wallpapers path. For getting as Pillow image object, use True as parameter.
# Wallpaper.set() Set wallpaper. Can be path of image or Pillow object. File type doesn't matter and path can be absolute or relative.
# Wallpaper.copy() - Copy current wallpaper. First parameter is directory and the second is file name. File extension should be JPG. Default directory is current directory and file name is 'wallpaper.jpg'
import time
from os import path, getenv, getcwd
from ctypes import windll
from shutil import copyfile
from PIL import Image
from tempfile import NamedTemporaryFile
import pyautogui


class Wallpaper:
    """A class used to change the desktop wallpaper"""
    # Get
    @staticmethod
    def get(returnImgObj=False):
        currentWallpaper = getenv(
            'APPDATA') + "\\Microsoft\\Windows\\Themes\\TranscodedWallpaper"
        if returnImgObj == True:
            return Image.open(currentWallpaper)
        else:
            tempFile = NamedTemporaryFile(mode="wb", suffix='.jpg').name
            copyfile(currentWallpaper, tempFile)
            return tempFile

    # Set
    @staticmethod
    def set(wallpaperToBeSet):
        # Check it is a file
        if path.isfile(wallpaperToBeSet):
            wallpaperToBeSet = path.abspath(wallpaperToBeSet)
            # If a JPG, set
            if wallpaperToBeSet.lower().endswith('.jpg') or wallpaperToBeSet.lower().endswith('.jpeg'):
                windll.user32.SystemParametersInfoW(
                    20, 0, path.abspath(wallpaperToBeSet), 3)
                return True
            # If not a JPG, convert and set
            else:
                image = Image.open(wallpaperToBeSet)
                with NamedTemporaryFile(mode="wb", suffix='.jpg') as tempFile:
                    image.save(tempFile, quality=100)
                    windll.user32.SystemParametersInfoW(
                        20, 0, path.abspath(tempFile), 3)
                return True

        # Check it is a Pillow object
        elif str(wallpaperToBeSet).find('PIL'):
            with NamedTemporaryFile(mode="wb", suffix='.jpg') as tempFile:
                Image.save(tempFile, quality=100)
                windll.user32.SystemParametersInfoW(
                    20, 0, path.abspath(tempFile), 3)
            return True
        else:
            return False

    # Copy
    @staticmethod
    def copy(copyTo=getcwd(), fileName='wallpaper.jpg'):
        return copyfile(Wallpaper.get(), path.join(path.abspath(copyTo), fileName))


if __name__ == '__main__':
    save_wallpaper = Wallpaper.get()

    Wallpaper.set("Change_Wallpaper.jpg")

    pyautogui.keyDown('winleft')
    pyautogui.press('d')
    pyautogui.keyUp('winleft')

    time.sleep(7)

    Wallpaper.set(save_wallpaper)
    time.sleep(7)


