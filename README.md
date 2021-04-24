# AptioBMPChanger
Change bitmaps in aptio iv firmware images

#### Warning
I am not responsible for damages of any kind. Use it at your own risk!

# Setup
#### Setup on Windows:
```
python -m venv venv && venv\Scripts\pip install flask tableprint requests
```

#### Run on Windows:
```
python execution_server.py
python main.py
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
