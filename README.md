# Getting Started with Mapout Skills App

## Installing Python 

To successfully run this application, you need to first setup your Python development environment. Specifically, this app requires:
-Python 3
-VS Code application
-VS Code Python extension

1. Install Visual Studio Code and the Python Extension
If you have not already done so, install VS Code.

Next, install the Python extension for VS Code from the Visual Studio Marketplace. For additional details on installing extensions, see Extension Marketplace. The Python extension is named Python and it's published by Microsoft.

2. Installing Python Interpreter on the system

Installing the latest version of Python is recommended, even though the minimum version of Python 3.6 is sufficient to run majority of the features.

### How to install?
Windows
Install Python from python.org. You can typically use the Download Python button that appears first on the page to download the latest version.

Note: If you don't have admin access, an additional option for installing Python on Windows is to use the Microsoft Store. The Microsoft Store provides installs of Python 3.6, Python 3.7, Python 3.8, Python 3.9, and Python 3.10.

For additional information about using Python on Windows, see Using Python on Windows at Python.org

macOS
The system install of Python on macOS is not supported. Instead, a package management system like Homebrew is recommended. To install Python using Homebrew on macOS use brew install python3 at the Terminal prompt.

Note On macOS, make sure the location of your VS Code installation is included in your PATH environment variable. 

Linux
The built-in Python 3 installation on Linux works well, but to install other Python packages you must install pip with get-pip.py. 

Other options
Data Science/Machine Learning: If your primary purpose for using Python is Data Science, then you might consider a download from Anaconda. Anaconda provides not just a Python interpreter, but many useful libraries and tools for data science.


## Verify the Python installation
To verify that you've installed Python successfully on your machine, run one of the following commands (depending on your operating system):

Linux/macOS: open a Terminal Window and type the following command:

### `python3 --version`

Windows: open a command prompt and run the following command:

### `py -3 --version`

If the installation was successful, the output window should show the version of Python that you installed.


## Available Scripts

In the project directory, you can run:

### `npm start` 
to download the dependencies on node js

### `python3 -m pip install requirements.txt`
( In case your python version < 3.4, you may need to download and install "pip" manually)
