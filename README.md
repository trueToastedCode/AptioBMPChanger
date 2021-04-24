# AptioBMPChanger
Change bitmaps in aptio iv firmware images

#### Warning
I am not responsible for damages of any kind. Use it at your own risk!

#### Usage
Open your rom in UEFITool. Search for HEX Patern (Topbar->Action->Search) ```20030000580200000100``` or ```00040000000300000100 ```. It means 800x600 or 1024x768 with one plane as part of the BMP file header.

It can be generated like that:
```
from bytes_helper import *
print(swap('{:08x}'.format(width)) + swap('{:08x}'.format(height)) + swap('{:04x}'.format(1))))
```

It should find some offset. It has to be in the FV_MAIN_NESTED file, followed by another file with a compressed raw section. Set the GUID of the FV_MAIN_NESTED file into the main.py in the variable "FV_MAIN_NESTED_GUID". Set the GUID of the second file into the "SPLASH_GUID" variable below. 

![search](https://user-images.githubusercontent.com/44642574/115959410-69e8ff00-a50c-11eb-95f6-a24f0d0e2414.PNG)

Then play your rom into the Roms folder and set filename of the rom into the ROM_PATH variable. On Windows, you need to correct to forward slashes to backward slashes in the ROM_PATH, ARCHIVE_PATH and BMP_PATH variables.

#### Creating an image replacement
First of all, if you just want a patched rom the make an image with the same resolution and depth. I notices that when creating an BMP with Photoshop like that, the filesize is 2 bytes bigger than the original BMP. They were no part of the image so i deleted them and corrected the header of the file by adopting the file size. I also notices, that the ROM BMP's have some stuff i don't know why in the reserved offsets and between the header and pixel data. I ended to simply copy them into my replacement BMP (Correct the header if sile size changed!).

I dont know is this is really possible, but if you replace the image with an image that is bigger, the tool will write the replecement splash file, but you have to replace it with UBU because this script cannot parse the volumes and correct the headers.

# Setup
#### Setup on Windows:
```
python -m venv venv && venv\Scripts\pip install flask tableprint requests
```

#### Run on Windows:
```
venv\Scripts\python execution_server.py
venv\Scripts\python main.py
```

#### Setup on Linux/macOS:
```
python -m venv venv && venv/bin/pip install tableprint requests
```
Setup Wine(Liunx)/Wineskin(MacOS) with Python3 for Windows, Open Cmd:
```
python -m pip install flask
```

#### Run on Linux/MacOS:
In Wine cmd:
```
cd "Path to project" && python execution_server.py
```
In Linux/MacOS:
```
python main.py
```
