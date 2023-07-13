# PiCam

An user interface to control Princeton  scientifics camera 

This software is not associated with TELEDYNE . Use it at your own risk.

it use 
PICam™ 5.x SDK from Teledyne
inspered from https://github.com/sliakat/SpeReadPy
The path of dll librairy is :
libPath: str='C:/Program Files/Princeton Instruments/PICam/Runtime/picam.dll

If you install Picam sdk somewhere else please change the path in picam.py line 337


It can make plot profile and data measurements analysis by using :
https://github.com/julienGautier77/visu
## It is tested :
on win 10 64 bits (AMD64)

with python 3.10.12 based on conda

On a PIXIS 1024 

Picam dll :  5.13.3.2211


## Requirements
*   python >3.8
*   PyQt6
*   visu 2023.07
*   picam installer 5.

## Installation
install PICam skd install for Teledyne (see https://github.com/sliakat/SpeReadPy)
install visu :
pip install git+https://github.com/julienGautier77/visu

## Usage

    appli = QApplication(sys.argv)
    import princeton 
    e = princeton.Ropper()  
    e.show()
    appli.exec_()      
