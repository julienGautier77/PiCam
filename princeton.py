# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 23:14:46 2001
on conda prompt 

pip install visu
if problem Dll copy  dll in the folder , check python version if >3.7 change in picam.py self.picamLib = ctypes.CDLL(pathToLib, winmode=0)#cdll.LoadLibrary(pathToLib)
@author: juliengautier
modified 2019/08/13 : add position RSAI motors
modified 2021/06/16 : add opining by serial number
modified 2023/07/07 : PyQt6
"""
import __init__ 
__version__=__init__.__version__
__author__=__init__.__author__
version=__version__

from PyQt6.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QWidget,QPushButton,QToolButton,QLayout,QMenu,QDockWidget,QDoubleSpinBox,QGridLayout, QFileDialog
from PyQt6.QtWidgets import QComboBox,QSlider,QLabel,QSpinBox,QInputDialog
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import sys,time
import numpy as np
import pathlib
import os
import pyqtgraph as pg 
import platform
try :
    import picam
except:
    print('can not control ropper camera: cameraClass or picam_types module is missing')   
    
import qdarkstyle
from visu import SEE
from PIL import Image


class ROPPER(QWidget):

    signalData=QtCore.pyqtSignal(object)
    
    def __init__(self,cam=None,confFile='confCCD.ini',**kwds):
        
        super(ROPPER, self).__init__()
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.version = version
        self.icon = str(p.parent) + sepa+'icons' +sepa
        self.configMotorPath = "./fichiersConfig/"
        self.configMotName = 'configMoteurRSAI.ini'
        self.confMotorPath = self.configMotorPath+self.configMotName
        self.confMot = QtCore.QSettings(str(p.parent / self.confMotorPath), QtCore.QSettings.Format.IniFormat)
        self.nbcam = cam
        self.isConnected = False
        self.kwds = kwds
        
        if "confpath" in kwds:
            self.confpath = kwds["confpath"]
        else  :
            self.confpath = None
        
        
        if self.confpath == None:
            self.confpath = str(p.parent / confFile) # ini file with global path
        
        self.conf = QtCore.QSettings(self.confpath, QtCore.QSettings.Format.IniFormat) # ini file 
        
        
        self.kwds["confpath"] = self.confpath

        if "affLight" in kwds:
            self.light = kwds["affLight"]
        else:
            self.light = False
        if "aff" in kwds: #  affi of Visu
            self.aff = kwds["aff"]
        else: 
            self.aff="right"   
        if "separate" in kwds:

            self.separate = kwds["separate"]
        else: 
            self.separate = False    

        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6')) # qdarkstyle :  black windows style

        self.iconPlay = self.icon+'Play.png'
        self.iconSnap = self.icon+'Snap.png'
        self.iconStop = self.icon+'Stop.png'
        self.iconPlay = pathlib.Path(self.iconPlay)
        self.iconPlay = pathlib.PurePosixPath(self.iconPlay)
        self.iconStop = pathlib.Path(self.iconStop)
        self.iconStop = pathlib.PurePosixPath(self.iconStop)
        self.iconSnap = pathlib.Path(self.iconSnap)
        self.iconSnap = pathlib.PurePosixPath(self.iconSnap)
        self.nbShot = 1
        self.camIsRunnig = False
        
        if self.nbcam == None:
            # self.camID=None
            self.nbcam = "camDefault"
        
        self.ccdName = self.conf.value(self.nbcam+"/nameCDD")
        self.serial = self.conf.value(self.nbcam+"/serial")
       
        self.initCam()
        self.setup()
        self.itrig = 0
        self.actionButton()
        self.camIsRunnig = False
       
    def initCam(self):
        self.cam = picam.Camera()
        camProp = self.cam.getAvailableCameras()
        #print('Camera name is : ' ,str(self.ccdName))
        self.cameraType = 'Princeton Instrument'
        try :
            self.cam.OpenCamerabySerial(serial=self.serial)
            self.isConnected = True
        except:
            self.isConnected = False
         
    def update_temp(self, temp=None,stat=None):
       
        if temp == None:
            temp = 123
        if stat == 2 :
            tLocked = True
            self.tempBox.setStyleSheet('font :bold 10pt;color: green')
        else :
            tLocked = False
            self.tempBox.setStyleSheet('font :bold 10pt;color: red')
        
        self.tempBox.setText('%.1f °C' % temp)
        
    def setup(self): 
        """ user interface definition: 
        """
        vbox1 = QVBoxLayout() # 
        hbox1 = QHBoxLayout() # horizontal layout pour run snap stop
        self.sizebuttonMax = 30
        self.sizebuttonMin = 30

        self.runButton = QToolButton(self)
        self.runButton.setMaximumWidth(self.sizebuttonMax)
        self.runButton.setMinimumWidth(self.sizebuttonMax)
        self.runButton.setMaximumHeight(self.sizebuttonMax)
        self.runButton.setMinimumHeight(self.sizebuttonMax)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: green;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"% (self.iconPlay,self.iconPlay) )
        
        self.snapButton = QToolButton(self)
        self.snapButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        menu = QMenu()
        menu.addAction('set nb of shot',self.nbShotAction)
        self.snapButton.setMenu(menu)
        self.snapButton.setMaximumWidth(self.sizebuttonMax)
        self.snapButton.setMinimumWidth(self.sizebuttonMax)
        self.snapButton.setMaximumHeight(self.sizebuttonMax)
        self.snapButton.setMinimumHeight(self.sizebuttonMax)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: green;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"% (self.iconSnap,self.iconSnap) )
        
        self.stopButton = QToolButton(self)
        self.stopButton.setMaximumWidth(self.sizebuttonMax)
        self.stopButton.setMinimumWidth(self.sizebuttonMax)
        self.stopButton.setMaximumHeight(self.sizebuttonMax)
        self.stopButton.setMinimumHeight(self.sizebuttonMax)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"% (self.iconStop,self.iconStop) )
        self.stopButton.setEnabled(False)
        
        hbox1.addWidget(self.runButton)
        hbox1.addWidget(self.snapButton)
        hbox1.addWidget(self.stopButton)
        
        hbox1.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)#setFixedSize)#
        hbox1.setContentsMargins(0, 0, 0, 0)
        hbox1.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        vbox1.addLayout(hbox1)
        vbox1.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        vbox1.setContentsMargins(0, 20, 10, 10)
        
        self.widgetControl = QWidget(self)
        self.widgetControl.setLayout(vbox1)
        self.dockControl = QDockWidget(self)
        self.dockControl.setWidget(self.widgetControl)
        
        self.trigg = QComboBox()
        self.trigg.setMaximumWidth(90)
        self.trigg.addItem('OFF')
        self.trigg.addItem('ON')
        self.trigg.setStyleSheet('font :bold 10pt;color: white')
        self.labelTrigger = QLabel('Trig')
        self.labelTrigger.setMaximumWidth(50)
        # self.labelTrigger.setMinimumHeight(50)
        self.labelTrigger.setStyleSheet('font :bold  10pt')
        self.itrig = self.trigg.currentIndex()
        hbox2 = QHBoxLayout()
        hbox2.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        hbox2.setContentsMargins(0, 20, 10, 10)
        hbox2.addWidget(self.labelTrigger)
        hbox2.addWidget(self.trigg)
        self.widgetTrig = QWidget(self)
        self.widgetTrig.setLayout(hbox2)
        self.dockTrig = QDockWidget(self)
        self.dockTrig.setWidget(self.widgetTrig)
        
        self.labelExp = QLabel('Exposure (ms)')
        self.labelExp.setStyleSheet('font :bold  10pt')
        self.labelExp.setMaximumWidth(140)
        self.labelExp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.hSliderShutter = QSlider(Qt.Orientation.Horizontal)
        self.hSliderShutter.setMaximumWidth(60)
        self.shutterBox = QSpinBox()
        self.shutterBox.setStyleSheet('font :bold  8pt')
        self.shutterBox.setMaximumWidth(120)
        
        self.shutterBox.setMaximum(1500)
        self.hSliderShutter.setMaximum(1500)
        
        hboxShutter = QHBoxLayout()
        hboxShutter.setContentsMargins(0, 0, 0, 5)
        hboxShutter.setSpacing(10)
        vboxShutter=QVBoxLayout()
        vboxShutter.setSpacing(0)
        vboxShutter.addWidget(self.labelExp)#,Qt.AlignLef)
        
        hboxShutter.addWidget(self.hSliderShutter)
        hboxShutter.addWidget(self.shutterBox)

        vboxShutter.addLayout(hboxShutter)
        vboxShutter.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        vboxShutter.setContentsMargins(0, 0, 10, 0)
        vboxShutter.setSpacing(2)
        
        self.widgetShutter = QWidget(self)
        self.widgetShutter.setLayout(vboxShutter)
        self.dockShutter = QDockWidget(self)
        self.dockShutter.setWidget(self.widgetShutter)
        
        self.labelGain = QLabel('Gain')
        self.labelGain.setStyleSheet('font :bold  10pt')
        self.labelGain.setMaximumWidth(140)
        self.labelGain.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.hSliderGain = QSlider(Qt.Orientation.Horizontal)
        self.hSliderGain.setMaximumWidth(60)
        self.gainBox = QSpinBox()
        self.gainBox.setStyleSheet('font :bold  8pt')
        self.gainBox.setMaximumWidth(120)
        
        hboxGain = QHBoxLayout()
        hboxGain.setContentsMargins(0, 0, 0, 5)
        hboxGain.setSpacing(10)
        vboxGain=QVBoxLayout()
        vboxGain.setSpacing(0)
        vboxGain.addWidget(self.labelGain)

        hboxGain.addWidget(self.hSliderGain)
        hboxGain.addWidget(self.gainBox)
        
        vboxGain.addLayout(hboxGain)
        vboxGain.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        
        hMainLayout = QHBoxLayout()
        
        if self.light is False: # light option : not all the option af visu 
            from visu import SEE
            self.visualisation = SEE(parent=self,name=self.nbcam,**self.kwds) ## Widget for visualisation and tools  self.confVisu permet d'avoir plusieurs camera et donc plusieurs fichier ini de visualisation
        else:
            from visu import SEELIGHT
            self.visualisation = SEELIGHT(parent=self,name=self.nbcam,**self.kwds)

        self.dockTrig.setTitleBarWidget(QWidget())        
        self.dockControl.setTitleBarWidget(QWidget()) # to avoid tittle
        self.dockShutter.setTitleBarWidget(QWidget())
        
        if self.separate is True: # control camera button is not on the menu but in a widget at the left or right of the display screen
            self.dockTrig.setTitleBarWidget(QWidget())
            if self.aff == 'left':
                self.visualisation.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockControl)
                self.visualisation.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockTrig)
                self.visualisation.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockShutter)
                
            else:
                self.visualisation.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockControl)
                self.visualisation.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockTrig)
                self.visualisation.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockShutter)
                
        else:
        #self.dockControl.setFeatures(QDockWidget.DockWidgetMovable)
            self.visualisation.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,self.dockControl)
            self.visualisation.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,self.dockTrig)
            self.visualisation.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,self.dockShutter)
            
        hMainLayout.addWidget(self.visualisation)       

        self.settingButton = QToolButton(self)
        self.settingButton.setMaximumWidth(self.sizebuttonMax+30)
        self.settingButton.setMinimumWidth(self.sizebuttonMax+30)
        self.settingButton.setMaximumHeight(self.sizebuttonMax)
        self.settingButton.setMinimumHeight(self.sizebuttonMax)
        self.settingButton.setText('Cam Set.')
        hbox1.addWidget(self.settingButton)
        
        self.tempButton = QToolButton(self)
        self.tempButton.setMaximumWidth(self.sizebuttonMax+10)
        self.tempButton.setMinimumWidth(self.sizebuttonMax+10)
        self.tempButton.setMaximumHeight(self.sizebuttonMax)
        self.tempButton.setMinimumHeight(self.sizebuttonMax)
        self.tempButton.setText('Temp')
        hbox1.addWidget(self.tempButton)
        self.tempBox = QLabel('?')
        hbox1.addWidget(self.tempBox)
        self.setLayout(hMainLayout)
        self.setContentsMargins(0, 0, 0, 0)

        if self.isConnected is True: 
            
            self.settingWidget = SETTINGWIDGET(cam=self.cam,visualisation=self.visualisation, conf=self.conf,nbcam=self.nbcam)

            self.sh = int(self.conf.value(self.nbcam+"/shutter")   ) # set exp time in shutter box 
            self.shutterBox.setValue(int(self.sh))
            self.hSliderShutter.setValue(int(self.sh) )

            self.threadTemp = ThreadTemperature(cam=self.cam,parent= self) # start temperarute reading
            self.threadTemp.stopTemp = False
            self.threadTemp.TEMP.connect(self.update_temp)
            self.threadTemp.start()
            
            self.cam.setParameter("PicamParameter_CleanCycleCount", int(1))
            self.cam.setParameter("PicamParameter_CleanCycleHeight", int(1))
            
            # self.cam.setParameter("TriggerResponse"     , int(1)) # pas de trig
            self.cam.setParameter("PicamParameter_TriggerDetermination", int(1))
            self.w = self.cam.getParameter("PicamParameter_ActiveWidth")
            self.h = self.cam.getParameter("PicamParameter_ActiveHeight")
            
            self.cam.setROI(0, self.w, 1, 0, self.h, 1, 0) # set full frame ROI 
            self.cam.setParameter("PicamParameter_ExposureTime", int(self.sh))
            
            self.dimx = self.w
            self.dimy = self.h
            #print('adc',self.cam.getParameter("PicamParameter_AdcSpeed"))
            #print('ShutterTimingMode',self.cam.getParameter("PicamParameter_ShutterTimingMode"))
            self.cam.SetTemperature(15)
            self.serial = self.cam.getSerialNumber()
            self.tempWidget = TEMPWIDGET(cam=self.cam)
            self.threadRunAcq = ThreadRunAcq(self)
            self.threadOneAcq = ThreadOneAcq(self)
            self.threadRunAcq.newDataRun.connect(self.Display)    
            self.threadOneAcq.newDataRun.connect(self.Display)  
            
        self.setWindowTitle(self.cameraType+"   " + self.ccdName+ ' :   s/n:  '+str(self.serial)+'     v.'+ self.version+"   " +'Visu v.'+self.visualisation.version)
    
    def shutter (self):
        '''set exposure time 
        '''
        self.sh = self.shutterBox.value() # 
        self.hSliderShutter.setValue(int(self.sh) )# set value of slider
        self.cam.SetExposure(int(self.sh))
        time.sleep(0.1)
        self.conf.setValue(self.nbcam+"/shutter",float(self.sh))
        self.conf.sync()
    
    def mSliderShutter(self): # for shutter slider 
        self.sh = self.hSliderShutter.value()
        self.shutterBox.setValue(int(self.sh))
        self.cam.SetExposure(int(self.sh))
       
        time.sleep(0.1)
        self.conf.setValue(self.nbcam+"/shutter",float(self.sh))
    
    def actionButton(self): 
        '''action when button are pressed
        '''
        self.runButton.clicked.connect(self.acquireMultiImage)
        self.snapButton.clicked.connect(self.acquireOneImage)
        self.stopButton.clicked.connect(self.stopAcq)      
        self.shutterBox.editingFinished.connect(self.shutter)    
        self.hSliderShutter.sliderReleased.connect(self.mSliderShutter)
        self.trigg.currentIndexChanged.connect(self.Trigger)
        self.tempButton.clicked.connect(lambda:self.open_widget(self.tempWidget) )
        self.settingButton.clicked.connect(lambda:self.open_widget(self.settingWidget) )
        
    
    def acquireOneImage(self):
        '''Start on acquisition
        '''
        self.imageReceived=False
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color:gray}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        self.hSliderShutter.setEnabled(False)
        self.shutterBox.setEnabled(False)
        self.threadOneAcq.newRun() # to set stopRunAcq=False
        self.threadOneAcq.start()
        self.camIsRunnig = True
        for child in self.settingWidget.findChildren(QPushButton):
            child.setEnabled(False)
        for child in self.settingWidget.findChildren(QComboBox):
            child.setEnabled(False)


    def acquireMultiImage(self):    
        ''' start the acquisition thread
        '''
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color:gray}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        self.hSliderShutter.setEnabled(False)
        self.shutterBox.setEnabled(False)
        for child in self.settingWidget.findChildren(QPushButton):
            child.setEnabled(False)
        for child in self.settingWidget.findChildren(QComboBox):
            child.setEnabled(False)    
        self.threadRunAcq.newRun() # to set stopRunAcq=False
        self.threadRunAcq.start()
        self.camIsRunnig = True 
    
    def stopAcq(self):
        
        self.cam.StopAcquisition()
        try:
            self.threadRunAcq.stopThreadRunAcq()
        except:
            pass
        try: 
            self.threadAcq.terminate()
        except:
            pass
        print('acquisition stopped')
        self.runButton.setEnabled(True)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: green;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(True)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{border-image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(True)
        self.hSliderShutter.setEnabled(True)
        self.shutterBox.setEnabled(True)
        for child in self.settingWidget.findChildren(QPushButton):
            child.setEnabled(True)
        for child in self.settingWidget.findChildren(QComboBox):
            child.setEnabled(True)
        self.camIsRunnig = False

    def Trigger(self):
    ## trig la CCD
    # work with pixis camera but not with mte camera     
    
   #  PicamTriggerDetermination_PositivePolarity       = 1,
   # PicamTriggerDetermination_NegativePolarity       = 2,
   # PicamTriggerDetermination_RisingEdge             = 3,
   # PicamTriggerDetermination_FallingEdge            = 4,
   # PicamTriggerDetermination_AlternatingEdgeRising  = 5,
   # PicamTriggerDetermination_AlternatingEdgeFalling = 6
   
    # PicamTriggerResponse_NoResponse               = 1,
    # PicamTriggerResponse_StartOnSingleTrigger     = 5,
    # PicamTriggerResponse_ReadoutPerTrigger        = 2,
    # PicamTriggerResponse_ShiftPerTrigger          = 3,
    # PicamTriggerResponse_GatePerTrigger           = 6,
    # PicamTriggerResponse_ExposeDuringTriggerPulse = 4
   
    # PicamTriggerSource_None     = 3, Pas DISPO pour PIXIS Et MTE
   #  PicamTriggerSource_Internal = 2,
   #  PicamTriggerSource_External = 1
   
   # PicamTriggerTermination_FiftyOhms     = 1,
   #  PicamTriggerTermination_HighImpedance = 2
        itrig = self.trigg.currentIndex()
        if itrig == 0:
            self.cam.setParameter("PicamParameter_TriggerResponse", int(1))
            self.cam.setParameter("PicamParameter_TriggerDetermination", int(3))
            # self.cam.setParameter("PicamParameter_TriggerSource",int(3)) # pas dispo 
            # self.cam.sendConfiguration()
            print ('trigger OFF')
        if itrig == 1:
            # self.cam.setParameter("PicamParameter_TriggerSource",int(1))
            self.cam.setParameter("PicamParameter_TriggerResponse", int(2))
            self.cam.setParameter("PicamParameter_TriggerDetermination", int(3)) 
            # self.cam.sendConfiguration()
            print ('Trigger ON ')
        #Úprint('trigger S R T',self.cam.getParameter("PicamParameter_TriggerDetermination"))
    
    def Display(self,data):
        '''Display data with Visu module
        '''
        # self.visualisation.newDataReceived(self.data) # send data to visualisation widget
        self.signalData.emit(data)
    
    def nbShotAction(self):
        '''
        number of snapShot
        '''
        nbShot, ok = QInputDialog.getInt(self,'Number of SnapShot ','Enter the number of snapShot ',value=self.nbShot,min=1)
        if ok:
            self.nbShot = int(nbShot)
            if self.nbShot <=0 :
               self.nbShot = 1

    def open_widget(self,fene):
        
        """ open new widget 
        """
        if fene.isWinOpen is False:
            #New widget"
            fene.show()
            fene.isWinOpen = True
        else:
            #fene.activateWindow()
            fene.raise_()
            fene.showNormal()
        
    def closeEvent(self,event):
        ''' closing window event (cross button)
        '''
        #print(' close')
        try :
            self.threadTemp.stopThreadTemp()
        except:
            print('no camera connected')
        #self.threadTemp.stopThreadTemp()
        self.cam.disconnect()
        
        time.sleep(0.2)      
        if self.isConnected is True:
            if self.settingWidget.isWinOpen is True:
                self.settingWidget.close()


class ThreadRunAcq(QtCore.QThread):
    
    newDataRun = QtCore.pyqtSignal(object)
    
    def __init__(self, parent):
        # super(ThreadRunAcq,self).__init__(parent)
        super().__init__()
        self.stopRunAcq = False
        self.parent = parent
        self.cam = self.parent.cam
    
    def newRun(self):
        self.stopRunAcq = False
    
    def run(self):
        print('-----> Start  multi acquisition')
        #print('threadexp',self.cam.GetExposure())
        # self.cam.Acquisition(timeout=2000)
        while True :
            if self.stopRunAcq:
                break
            if self.cam.IsAcquisitionRunning() is False:
                self.cam.Acquisition(N=1,timeout=120000)
                print('----->  Acquisition ')
                try :
                    data = self.cam.GetAcquiredData()
                    data = np.array(data, dtype=np.double)
                    self.data = np.rot90(data,3)
                    self.newDataRun.emit(data)
                  #  print('acquisition done')
                except :
                    pass
            else:
                print('acquisition en cours...')
    
    def stopThreadRunAcq(self):
        self.stopRunAcq = True
        self.cam.StopAcquisition()
        

class ThreadOneAcq(QtCore.QThread):
    newDataRun = QtCore.pyqtSignal(object)
    
    def __init__(self, parent):
        super().__init__()
        self.stopRunAcq = False
        self.parent = parent
        self.cam = self.parent.cam
        
    def newRun(self):
        self.stopRunAcq = False
    
    def run(self):
        print('-----> Start  ',self.parent.nbShot,' acquisition')
        #print('threadexp',self.cam.GetExposure())
        # self.cam.Acquisition(timeout=2000)
        for i in range(self.parent.nbShot) :
            if self.stopRunAcq:
                break
            if self.cam.IsAcquisitionRunning() is False:
                self.cam.Acquisition(N=1,timeout=120000)
                print('----->  Acquisition ')
                try :
                    data = self.cam.GetAcquiredData()
                    data = np.array(data, dtype=np.double)
                    self.data = np.rot90(data,3)
                    self.newDataRun.emit(data)
                  #  print('acquisition done')
                except :
                    pass
            else:
                print('acquisition en cours...')
        self.parent.stopAcq()

    def stopThreadRunAcq(self):
        self.stopRunAcq = True
        self.cam.StopAcquisition()


class ThreadTemperature(QtCore.QThread):
    """
    Thread pour la lecture de la temperature toute les 2 secondes
    """
    TEMP = QtCore.pyqtSignal(float,int) # signal pour afichage temperature

    def __init__(self, parent=None,cam=None):
        # super(ThreadTemperature,self).__init__(parent)
        super().__init__()
        self.cam    = cam
        self.stopTemp = False
        self.parent = parent

    def run(self):
        while self.cam.cam is not None  and self.parent.camIsRunnig == False:#¶and self.cam.IsAcquisitionRunning()==False:
            temp = self.cam.GetTemperature()
            time.sleep(1)
            stat = int(self.cam.GetTemperatureStatus())
            self.TEMP.emit(temp,stat)
            #print('satus',self.cam.GetTemperatureStatus(),temp)
            if self.stopTemp:
                break
                  
    def stopThreadTemp(self):
        self.stopTemp = True
        print ('stop thread temperature')  
        self.terminate()        


class TEMPWIDGET(QWidget):
    
    def __init__(self, cam=None,parent=None):
        super().__init__()
        # super(TEMPWIDGET, self).__init__(parent)
        self.cam = cam
        self.isWinOpen = False
        self.parent = parent
        self.setup()
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))

    def setup(self) :   
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('Temperature')
        self.vbox = QVBoxLayout()
        labelT = QLabel('Temperature')
        self.tempVal = QSpinBox(self)
        self.tempVal.setSuffix(" %s" % '°C')
        self.tempVal.setMaximum(21)
        self.tempVal.setMinimum(-40)
        self.tempVal.setValue(12)
        self.tempSet = QPushButton('Set')
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(labelT)
        self.hbox.addWidget(self.tempVal)
        self.hbox.addWidget(self.tempSet)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)
        self.tempSet.clicked.connect(self.SET)
        
    def SET(self):
        temp = self.tempVal.value()
        self.cam.SetTemperature(temp)
        # self.cam.sendConfiguration()
    
    def closeEvent(self, event):
        """ when closing the window
        """
        self.isWinOpen = False
        time.sleep(0.1)
        event.accept() 
        
        
class SETTINGWIDGET(QWidget):
    
    def __init__(self, cam = None, visualisation=None, parent=None, conf=None ,nbcam= None):
        
        super(SETTINGWIDGET, self).__init__(parent)
        self.cam = cam
        self.visualisation = visualisation
        self.isWinOpen = False
        self.parent = parent
        self.conf = conf
        self.nbcam = nbcam
        self.setup()
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.actionButton()
        self.roi1Is = False
        
    def setup(self) :

        self.dimx = self.cam.getParameter("PicamParameter_ActiveWidth")
        self.dimy = self.cam.getParameter("PicamParameter_ActiveHeight")
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('SETTINGS')
        self.vbox = QVBoxLayout()
        hboxShutter = QHBoxLayout()
        shutterLabel = QLabel('ShutterMode')
        self.shutterMode = QComboBox()
        self.shutterMode.setMaximumWidth(100)
        self.shutterMode.addItem('Normal')
        self.shutterMode.addItem('Always Close')
        self.shutterMode.addItem('Always Open')
        self.shutterMode.addItem('Open before trig')
        hboxShutter.addWidget(shutterLabel)
        hboxShutter.addWidget(self.shutterMode)
        self.vbox.addLayout(hboxShutter)
        
        hboxFrequency = QHBoxLayout()
        frequencyLabel = QLabel('Frequency')
        self.frequency = QComboBox()
        self.frequency.setMaximumWidth(100)
        self.frequency.addItem('Normal')
        self.frequency.addItem('Always Close')
        self.frequency.addItem('Always Open')
        hboxFrequency.addWidget(frequencyLabel)
        hboxFrequency.addWidget(self.frequency)
        self.vbox.addLayout(hboxFrequency)
        
        hboxROI = QHBoxLayout()
        hbuttonROI = QVBoxLayout()
        self.setROIButton = QPushButton('Set ROI')
        self.setROIFullButton = QPushButton('Set full Frame')
        self.setROIMouseButton = QPushButton('Mouse')
        hbuttonROI.addWidget(self.setROIButton)
        hbuttonROI.addWidget(self.setROIFullButton)
        hbuttonROI.addWidget(self.setROIMouseButton)
        hboxROI.addLayout(hbuttonROI)
        
        roiLay = QVBoxLayout()
        labelROIX = QLabel('ROI Xo')
        self.ROIX = QSpinBox(self)
        self.ROIX.setMinimum(0)
        self.ROIX.setMaximum(self.dimx)
        self.ROIX.setValue(int(self.conf.value(self.nbcam + "/x0")))
        
        self.ROIY = QSpinBox(self)
        self.ROIY.setMinimum(1)
        self.ROIY.setMaximum(self.dimy)
        self.ROIY.setValue(int(self.conf.value(self.nbcam + "/y0")))
        labelROIY = QLabel('ROI Yo')
        
        labelROIW = QLabel('ROI Dx')
        self.ROIW = QSpinBox(self)
        self.ROIW.setMinimum(0)
        self.ROIW.setMaximum(self.dimx)     
        self.ROIW.setValue(int(self.conf.value(self.nbcam + "/wroi")))
        
        labelROIH = QLabel('ROI Dy')
        self.ROIH = QSpinBox(self)
        self.ROIH.setMinimum(1)
        self.ROIH.setMaximum(self.dimy) 
        self.ROIH.setValue(int(self.conf.value(self.nbcam + "/hroi")))
        
        labelBinX = QLabel('Bin X')
        self.BINX = QSpinBox(self)
        self.BINX.setMinimum(1)
        self.BINX.setMaximum(self.dimx) 
        labelBinY = QLabel('Bin Y ')
        self.BINY = QSpinBox(self)
        self.BINY.setMinimum(1)
        self.BINY.setMaximum(self.dimy) 
        
        grid_layout = QGridLayout()
        grid_layout.addWidget(labelROIX,0,0)
        grid_layout.addWidget(self.ROIX,0,1)
        grid_layout.addWidget(labelROIY,1,0)
        grid_layout.addWidget(self.ROIY,1,1)
        grid_layout.addWidget(labelROIW,2,0)
        grid_layout.addWidget(self.ROIW,2,1)
        grid_layout.addWidget(labelROIH,3,0)
        grid_layout.addWidget(self.ROIH,3,1)
        grid_layout.addWidget(labelBinX,4,0)
        grid_layout.addWidget(self.BINX,4,1)
        grid_layout.addWidget(labelBinY,5,0)
        grid_layout.addWidget(self.BINY,5,1)
        
        roiLay.addLayout(grid_layout)
        hboxROI.addLayout(roiLay)
        self.vbox.addLayout(hboxROI)

        self.setLayout(self.vbox)
        self.r1 = 100
        self.roi1 = pg.RectROI([self.dimx/2,self.dimy/2], [2*self.r1, 2*self.r1],pen='r',movable=True)
        self.roi1.setPos([self.dimx/2-self.r1,self.dimy/2-self.r1])
        
    def actionButton(self):
        self.setROIButton.clicked.connect(self.roiSet)
        self.setROIFullButton.clicked.connect(self.roiFull)
        self.frequency.currentIndexChanged.connect(self.setFrequency)
        self.shutterMode.currentIndexChanged.connect(self.setShutterMode)
        self.setROIMouseButton.clicked.connect(self.mouseROI)
        self.roi1.sigRegionChangeFinished.connect(self.mousFinished)
        
    def mouseROI(self):
        self.visualisation.p1.addItem(self.roi1)
        self.roi1Is = True
        
    def mousFinished(self):
        
        posRoi = self.roi1.pos()
        sizeRoi = self.roi1.size()
        self.x0 = int(posRoi.x())
        self.wroi = int(sizeRoi.x())
        self.hroi = int(sizeRoi.y())
        self.y0 = int(posRoi.y())#+sizeRoi.y())
        self.ROIX.setValue(self.x0)
        self.ROIY.setValue(self.y0)
        self.ROIW.setValue(self.wroi)
        self.ROIH.setValue(self.hroi)
        
        self.conf.setValue(self.nbcam + "/x0",self.x0)
        self.conf.setValue(self.nbcam + "/y0",self.y0)
        self.conf.setValue(self.nbcam + "/wroi",self.wroi)
        self.conf.setValue(self.nbcam + "/hroi",self.hroi)
        
    def roiSet(self):
        
        self.x0 = int(self.ROIX.value())
        self.y0 = int(self.ROIY.value())
        self.w = int(self.ROIW.value())
        self.h = int(self.ROIH.value())
        self.binX = int(self.BINX.value())
        self.binY = int(self.BINY.value())

        # self.conf.setValue(self.nbcam + "/x0",self.x0)
        # self.conf.setValue(self.nbcam + "/y0",self.y0)
        # self.conf.setValue(self.nbcam + "/wroi",self.w)
        # self.conf.setValue(self.nbcam + "/hroi",self.h)

        self.y0 = abs (self.dimy - (self.y0 + self.h))
        
        if self.x0 <=0 :
            self.x0 = 0
        if self.y0 <= 0 :
            self.y0 = 0
        if self.h >= self.dimy :
            self.h = self.dimy
        if self.w >= self.dimx :
            self.w = self.dimx

        if self.roi1Is is True:
            self.visualisation.p1.removeItem(self.roi1)
            self.roi1Is = False
        if self.binX>1:
            self.w = int(np.floor(self.w/self.binX))*self.binX
        if self.binY>1:
            self.h = int(np.floor(self.h/self.binY)*self.binY)
        
        self.cam.setROI(self.y0, self.h, self.binY, self.x0, self.w, self.binX, 1)

    def roiFull(self):
        
        self.w = self.cam.getParameter("PicamParameter_ActiveWidth")
        self.h = self.cam.getParameter("PicamParameter_ActiveHeight")
        #self.w = self.cam.getParameter("paramSensorActiveWidth,")
        #self.h = self.cam.getParameter("paramSensorActiveHeight")
        self.cam.setROI(0, self.w, 1, 0, self.h, 1, 1) # full frame
        print("fullframe")
        if self.roi1Is is True:
            self.visualisation.p1.removeItem(self.roi1)
            self.roi1Is = False
        
    def setFrequency(self) :
        """
        set frequency reading in Mhz
        """          
        ifreq = self.freqency.currentIndex()
        if ifreq == 0:
             self.cam.setParameter("PicamParameter_AdcSpeed",0.1)
        if ifreq == 0:
             self.cam.setParameter("PicamParameter_AdcSpeed",1)
        if ifreq == 0:
             self.cam.setParameter("PicamParameter_AdcSpeed",2)
             
        print('adc frequency(Mhz)',self.cam.getParameter("AdcSpeed"))

    def setShutterMode(self):
        """ set shutter mode
        """
        ishut = self.shutterMode.currentIndex()
        print('shutter')
        if ishut == 0:
             self.cam.setParameter("PicamParameter_ShutterTimingMode",0)
        if ishut == 1:
             self.cam.setParameter("PicamParameter_ShutterTimingMode",1) 
        if ishut == 2:
             self.cam.setParameter("PicamParameter_ShutterTimingMode",2) 
        if ishut == 3:
             self.cam.setParameter("PicamParameter_ShutterTimingMode",3)
             print('OutputSignal',self.cam.getParameter("ShutterTimingMode"))
             
    def closeEvent(self, event):
        """ when closing the window
        """
        self.isWinOpen = False
        if self.roi1Is is True:
            self.visualisation.p1.removeItem(self.roi1)
            self.roi1Is = False
        time.sleep(0.1)
        
        event.accept() 
        
if __name__ == "__main__":       
    
    appli = QApplication(sys.argv)
    confpathVisu = 'C:/Users/GAUTIER/Desktop/python/princeton/confCCD.ini'
    appli.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    e = ROPPER(cam='MTE',motRSAI=True,spectro=False)#,confpath=confpathVisu)  
    e.show()
    appli.exec_()       
