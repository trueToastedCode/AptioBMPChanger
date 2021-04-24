# AptioBMPChanger
Change bitmaps in aptio iv firmware images

### Links
Tools named can be found here:
MMtool and more: https://www.tweaktownforum.com/forum/tech-support-from-vendors/gigabyte/30823-latest-overclocking-programs-system-info-benchmarking-stability-tools
UBU: https://mega.nz/folder/lLg2GLrA#SnZZd0WjHkULFHg7FESm8g
or https://mega.nz/folder/k4Z0FAra#hMIhuLoTte8IcwtiDibiAw

#### Warning
I am not responsible for damages of any kind. Use it at your own risk!

#### Usage
Open your rom in UEFITool. Search for HEX Patern (Topbar->Action->Search) ```20030000580200000100``` or ```00040000000300000100```. It means 800x600 or 1024x768 with one plane as part of the BMP file header.

It can be generated like that:
```
from bytes_helper import *
print(swap('{:08x}'.format(width)) + swap('{:08x}'.format(height)) + swap('{:04x}'.format(1))))
```

It should find some offset. It has to be in the FV_MAIN_NESTED file, followed by another file with a compressed raw section. Set the GUID of the FV_MAIN_NESTED file into the main.py in the variable "FV_MAIN_NESTED_GUID". Set the GUID of the second file into the "SPLASH_GUID" variable below. 

![search](https://user-images.githubusercontent.com/44642574/115959410-69e8ff00-a50c-11eb-95f6-a24f0d0e2414.PNG)

Then put your rom into the Roms folder and set filename of the rom into the ROM_PATH variable. On Windows, you need to correct to forward slashes to backward slashes in the ROM_PATH, ARCHIVE_PATH and BMP_PATH variables.

#### Creating an image replacement
First of all, if you just want a patched rom then make an image with the same resolution and depth. I noticed that when creating an BMP with Photoshop like that, the filesize is 2 bytes bigger than the original BMP. This is no part of the image so i deleted them and corrected the header of the file by adopting the file size. I also noticed, that the ROM BMP's have sometimes stuff i don't know why it is there in the reserved offsets and between the header and pixel data. I ended up to simply copy them into the replacement BMP's (Correct the header if file size changed!).

I dont know if this is really possible, but if you replace the image with an image that is bigger than the original, the tool will write the repaecement splash file, but you have to replace it with UBU because this script cannot parse the volumes and correct the headers.

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
venv/bin/python main.py
```
