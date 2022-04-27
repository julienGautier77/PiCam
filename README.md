# PiCam

PICam camera control is an user interface to control Princeton  scientifics camera 

This software is not associated with TELEDYNE . Use it at your own risk.

it use 
PICam™ 5.x SDK from teledyne

It can make plot profile and data measurements analysis by using :
https://github.com/julienGautier77/visu
## It is tested :
on win 11 64 bits (AMD64) 
with python 3.9.7 MSC v.1916 with anaconda installation
on a PIXI 1024 

## Requirements
*   python 3.x
*   Numpy
*   PyQt5
*   visu 2022.04

## Installation
install PICam install for teledyne



install visu :
pip install qdarkstyle (https://github.com/ColinDuquesnoy/QDarkStyleSheet.git)
pip install pyqtgraph (https://github.com/pyqtgraph/pyqtgraph.git)
pip install git+https://github.com/julienGautier77/visu



## Usage

    appli = QApplication(sys.argv)
    import princeton
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    e = Ropper()  
    e.show()
    appli.exec_()      
