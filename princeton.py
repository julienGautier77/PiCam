# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 23:14:46 2001
on conda prompt 

pip install qdarkstyle (https://github.com/ColinDuquesnoy/QDarkStyleSheet.git)
pip install pyqtgraph (https://github.com/pyqtgraph/pyqtgraph.git)
pip install visu

@author: juliengautier
modified 2019/08/13 : add position RSAI motors
modified 2021/06/16 : add opining by serial number
"""

__version__='2021.6'
__author__='julien Gautier'
version=__version__

from PyQt5.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QWidget,QPushButton
from PyQt5.QtWidgets import QComboBox,QSlider,QLabel,QSpinBox,QDoubleSpinBox,QGridLayout
from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys,time
import numpy as np
import pathlib,os
import pyqtgraph as pg 

try :
    import picam
except:
    print('can not control ropper camera: cameraClass or picam_types module is missing')   
    # pb load dll  install pvcam or copy paste all the folder dll 
import qdarkstyle
from visu import SEE



class ROPPER(QWidget):
    signalData=QtCore.pyqtSignal(object)
    
    def __init__(self,Nbcam=None,confFile='confCamera.ini',**kwds):
        self.isConnected=False
        super(ROPPER, self).__init__()
        p = pathlib.Path(__file__)
        sepa=os.sep
        
        
        self.icon=str(p.parent) + sepa+'icons' +sepa
        self.configMotorPath="./fichiersConfig/"
        self.configMotName='configMoteurRSAI.ini'
        self.confMotorPath=self.configMotorPath+self.configMotName
        self.confMot=QtCore.QSettings(str(p.parent / self.confMotorPath), QtCore.QSettings.IniFormat)
       
        
        self.kwds=kwds
        # self.kwds["conf"]=self.conf
        # self.kwds["confMot"]=self.confMot
        
        
        if "confpath" in kwds:
            self.confpath=kwds["confpath"]
        else  :
            self.confpath=None
        
        
        if self.confpath==None:
            self.confpath=str(p.parent / confFile) # ini file with global path
        
        self.conf=QtCore.QSettings(self.confpath, QtCore.QSettings.IniFormat) # ini file 
        
        
        self.kwds["confpath"]=self.confpath
        
        
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.iconPlay=pathlib.Path(self.icon+'Play.svg')
        self.iconPlay=pathlib.PurePosixPath(self.iconPlay)
        self.iconStop=pathlib.Path(self.icon+'Stop.svg')
        self.iconStop=pathlib.PurePosixPath(self.iconStop)
        self.rot=0
        
#        if camID==None: # si None on prend la première...
#            camID=0
#        if camID==0:
#            self.cam="cam0"
#        if camID==1:
#            self.cam="cam1"
#        if camID==2:
#            self.cam="cam1"
#        self.camID=int(camID)
#        print(self.camID)
        
        self.nbcam=Nbcam
        if self.nbcam==None:
            # self.camID=None
            self.nbcam="camDefault"
            
        
        
        self.ccdName=self.conf.value(self.nbcam+"/nameCDD")
        
       
        
        self.initCam()
        self.setup()
        self.itrig=0
        self.actionButton()
        self.camIsRunnig=False
       
    
    def initCam(self):
#        print('init cam')
        self.mte = picam.Camera()
        camProp=self.mte.getAvailableCameras()
        
        
        
        
        print('Camera name is : ' ,str(self.ccdName))
#         serialAvailable=camProp[2]
#         modelAvailable=camProp[0]
#         print(serialAvailable)
#         self.serial=self.conf.value(self.nbcam+"/serial")
# #        print(len(serialAvailable))
#         if self.serial==serialAvailable[0]:
#             self.camID=0
#         if len(serialAvailable)>1:
#             if self.serial==serialAvailable[1]:
#                 self.camID=1
#         if len(serialAvailable)>2:
#             if self.serial==serialAvailable[2]:
#                 self.camID=2
#         else: 
#             self.camID=0
        # print('camID',self.camID)
        # try :
        self.mte.OpenFirstCamera()
        # self.setWindowTitle(str(self.ccdName)+'  '+str(modelAvailable[self.camID])+ '  S/N : '+str(serialAvailable[self.camID])+'       v.'+ version)
        self.isConnected=True
        # except :
        #     try:"
        #         self.mte.OpenFirstCamera()
        #         self.setWindowTitle(str(self.ccdName)+ '  S/N :'+str(serialAvailable[0].decode())+'       v.'+ version)
        #         self.camID=0
        #         self.isConnected=True
        #     except:
        #         self.isConnected=False
        print('connected',self.isConnected)
        
        
        
        
    def update_temp(self, temp=None):
        if temp == None:
            temp = self.mte.GetTemperature()
        self.tempBox.setText('%.1f °C' % temp)
        
        
    def setup(self):  
        """ user interface definition: 
        """
        
        cameraWidget=QWidget()
        
        vbox1=QVBoxLayout() 
       
        self.camName=QLabel(self.ccdName,self)
        self.camName.setAlignment(Qt.AlignCenter)
        
        self.camName.setStyleSheet('font :bold  12pt;color: white')
        self.camName.setMaximumWidth(80)
        vbox1.addWidget(self.camName)
        
        hbox1=QHBoxLayout() # horizontal layout pour run et stop
        self.runButton=QPushButton(self)
        self.runButton.setMaximumWidth(60)
        self.runButton.setMinimumHeight(60)
        
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: green;}""QPushButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}"% (self.iconPlay,self.iconPlay) )
        self.stopButton=QPushButton(self)
        
        self.stopButton.setMaximumWidth(60)
        self.stopButton.setMinimumHeight(60)
        
        self.stopButton.setStyleSheet("QPushButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"% (self.iconStop,self.iconStop) )
        self.stopButton.setEnabled(False)
        
        hbox1.addWidget(self.runButton)
        hbox1.addWidget(self.stopButton)
        
        vbox1.addLayout(hbox1)
        
        self.trigg=QComboBox()
        self.trigg.setMaximumWidth(60)
        self.trigg.addItem('OFF')
        self.trigg.addItem('ON')
        self.labelTrigger=QLabel('Trigger')
        self.labelTrigger.setMaximumWidth(60)
        self.itrig=self.trigg.currentIndex()
        
        hbox2=QHBoxLayout()
        hbox2.addWidget(self.labelTrigger)
        hbox2.addWidget(self.trigg)
        
        vbox1.addLayout(hbox2)
        
        self.labelExp=QLabel('Exposure (ms)')
        self.labelExp.setMaximumWidth(120)
        self.labelExp.setAlignment(Qt.AlignCenter)
        vbox1.addWidget(self.labelExp)
        self.hSliderShutter=QSlider(Qt.Horizontal)
        self.hSliderShutter.setMinimum(50)
        self.hSliderShutter.setMaximum(100000)
        if self.isConnected==True:
            self.hSliderShutter.setValue(int(self.mte.GetExposure()))
        self.hSliderShutter.setMaximumWidth(80)
        self.shutterBox=QSpinBox()
        self.shutterBox.setMinimum(50)
        self.shutterBox.setMaximum(100000)

        if self.isConnected==True:
            self.shutterBox.setValue(int(self.mte.GetExposure()))
        hboxShutter=QHBoxLayout()
        hboxShutter.addWidget(self.hSliderShutter)
        hboxShutter.addWidget(self.shutterBox)
        vbox1.addLayout(hboxShutter)
        
        hboxTemp=QHBoxLayout()
        self.tempButton=QPushButton('Temp')
        self.tempButton.setMaximumWidth(80)
        hboxTemp.addWidget(self.tempButton)
        self.tempBox=QLabel('?')
        hboxTemp.addWidget(self.tempBox)
        vbox1.addLayout(hboxTemp)
        
        self.settingButton=QPushButton('Settings')
        vbox1.addWidget(self.settingButton)
                        
        vbox1.addStretch(1)
        cameraWidget.setLayout(vbox1)
        cameraWidget.setMinimumSize(150,200)
        cameraWidget.setMaximumSize(150,900)
        hMainLayout=QHBoxLayout()
        hMainLayout.addWidget(cameraWidget)
        
       
        self.visualisation=SEE(parent=self,name=self.nbcam,**self.kwds) ## Widget for visualisation and tools 
        
        vbox2=QVBoxLayout() 
        vbox2.addWidget(self.visualisation)
        hMainLayout.addLayout(vbox2)
        if self.isConnected==True:
            self.settingWidget=SETTINGWIDGET(mte=self.mte,visualisation=self.visualisation)
        
        self.setLayout(hMainLayout)
        
        
        if self.isConnected==True: 
            
            self.sh=int(self.conf.value(self.nbcam+"/shutter")   )
            
            self.threadTemp = ThreadTemperature(mte=self.mte)
            self.threadTemp.stopTemp=False
            self.threadTemp.TEMP.connect(self.update_temp)
            self.threadTemp.start()
            
            self.mte.setParameter("PicamParameter_CleanCycleCount"     , int(1))
            self.mte.setParameter("PicamParameter_CleanCycleHeight"    , int(1))
            
            # self.mte.setParameter("TriggerResponse"     , int(1)) # pas de trig
            self.mte.setParameter("PicamParameter_TriggerDetermination", int(1))
            self.w = self.mte.getParameter("PicamParameter_ActiveWidth")
            self.h = self.mte.getParameter("PicamParameter_ActiveHeight")
            
            self.mte.setROI(0, self.w, 1, 0, self.h, 1, 0) # full frame
            self.mte.setParameter("PicamParameter_ExposureTime", int(self.sh))
            
            self.dimx=self.w
            self.dimy=self.h
            print('adc',self.mte.getParameter("PicamParameter_AdcSpeed"))
            print('ShutterTimingMode',self.mte.getParameter("PicamParameter_ShutterTimingMode"))
            self.mte.SetTemperature(20)
            # self.mte.sendConfiguration()
            self.tempWidget=TEMPWIDGET(mte=self.mte)
            
            self.threadRunAcq=ThreadRunAcq(self)
            self.threadRunAcq.newDataRun.connect(self.Display)    
        
    def shutter (self):
        '''set exposure time 
        '''
        self.sh=self.shutterBox.value() # 
        self.hSliderShutter.setValue(int(self.sh) )# set value of slider
        # self.mte.SetExposure(int(self.sh))
        self.mte.setParameter("PicamParameter_ExposureTime",self.sh)
        time.sleep(0.1)
        self.conf.setValue(self.nbcam+"/shutter",float(self.sh))
        self.conf.sync()
    
    def mSliderShutter(self): # for shutter slider 
        self.sh=self.hSliderShutter.value()
        self.shutterBox.setValue(int(self.sh))
        self.mte.SetExposure(int(self.sh))
       
        time.sleep(0.1)
        self.conf.setValue(self.nbcam+"/shutter",float(self.sh))
    
    def actionButton(self): 
        '''action when button are pressed
        '''
        self.runButton.clicked.connect(self.acquireMultiImage)
        self.stopButton.clicked.connect(self.stopAcq)      
        self.shutterBox.editingFinished.connect(self.shutter)    
        self.hSliderShutter.sliderReleased.connect(self.mSliderShutter)
        self.trigg.currentIndexChanged.connect(self.TrigA)
        self.tempButton.clicked.connect(lambda:self.open_widget(self.tempWidget) )
        self.settingButton.clicked.connect(lambda:self.open_widget(self.settingWidget) )
        
    
    def acquireMultiImage(self):    
        ''' start the acquisition thread
        '''
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconPlay,self.iconPlay))
        
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QPushButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}"%(self.iconStop,self.iconStop) )
        
        self.trigg.setEnabled(False)
        self.hSliderShutter.setEnabled(False)
        self.shutterBox.setEnabled(False)
        
        self.threadRunAcq.newRun() # to set stopRunAcq=False
        self.threadRunAcq.start()
        self.camIsRunnig=True 
        
    
    def stopAcq(self):
        
        self.mte.StopAcquisition()
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
        self.runButton.setStyleSheet("QPushButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}"%(self.iconPlay,self.iconPlay))
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("QPushButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QPushButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(True)
        self.hSliderShutter.setEnabled(True)
        self.shutterBox.setEnabled(True)
    
    def TrigA(self):
    ## trig la CCD
    
    
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
        itrig=self.trigg.currentIndex()
        if itrig==0:
            self.mte.setParameter("PicamParameter_TriggerResponse", int(1))
            self.mte.setParameter("PicamParameter_TriggerDetermination", int(2))
            # self.mte.setParameter("PicamParameter_TriggerSource",int(3)) # pas dispo 
            # self.mte.sendConfiguration()
            print ('trigger OFF')
        if itrig==1:
            # self.mte.setParameter("PicamParameter_TriggerSource",int(1))
            self.mte.setParameter("PicamParameter_TriggerResponse", int(2))
            self.mte.setParameter("PicamParameter_TriggerDetermination", int(2)) 
            # self.mte.sendConfiguration()
            print ('Trigger ON ')
        print('trigger S R T',self.mte.getParameter("PicamParameter_TriggerResponse"))
    
    def Display(self,data):
        '''Display data with Visu module
        '''
        
        
       
        # self.visualisation.newDataReceived(self.data) # send data to visualisation widget
        self.signalData.emit(data)
    
    
    def open_widget(self,fene):
        
        """ open new widget 
        """
        
        if fene.isWinOpen==False:
            #New widget"
            fene.show()
            fene.isWinOpen=True
    
        else:
            #fene.activateWindow()
            fene.raise_()
            fene.showNormal()
        
    def closeEvent(self,event):
        ''' closing window event (cross button)
        '''
        print(' close')
        try :
            self.threadTemp.stopThreadTemp()
        except:
            print('no camera connected')
        #self.threadTemp.stopThreadTemp()
        self.mte.disconnect()
        
        time.sleep(0.2)      
        if self.isConnected==True:
            if self.settingWidget.isWinOpen==True:
                self.settingWidget.close()


class ThreadRunAcq(QtCore.QThread):
    
    newDataRun=QtCore.Signal(object)
    
    def __init__(self, parent):
        # super(ThreadRunAcq,self).__init__(parent)
        super().__init__()
        self.stopRunAcq=False
        self.parent=parent
        self.mte = self.parent.mte
    def newRun(self):
        self.stopRunAcq=False
    
    def run(self):
        
        print('-----> Start  multi acquisition')
        print('threadexp',self.mte.GetExposure())
        # self.mte.Acquisition(timeout=2000)
        while True :

            if self.stopRunAcq:
                break
            if self.mte.IsAcquisitionRunning()==False:
                self.mte.Acquisition(N=1,timeout=120000)
                
                print('----->  Acquisition ')
                try :
                    data = self.mte.GetAcquiredData()
                    data = np.array(data, dtype=np.double)
                    self.data=np.rot90(data,1)
                    self.newDataRun.emit(data)
                  #  print('acquisition done')
                except :
                    pass
            else:
                print('acquisition en cours...')
    
    def stopThreadRunAcq(self):
        self.stopRunAcq=True
        self.mte.StopAcquisition()
        
        
class ThreadTemperature(QtCore.QThread):
    """
    Thread pour la lecture de la temperature toute les 2 secondes
    """
    TEMP =QtCore.pyqtSignal(float) # signal pour afichage temperature

    def __init__(self, parent=None,mte=None):
        # super(ThreadTemperature,self).__init__(parent)
        super().__init__()
        self.mte    = mte
        self.stopTemp=False
        
    def run(self):
        while self.mte.cam is not None:
            temp = self.mte.GetTemperature()
            time.sleep(2)
            self.TEMP.emit(temp)
            if self.stopTemp:
                break
            
            
    def stopThreadTemp(self):
        self.stopTemp=True
        print ('stop thread temperature')  
        self.terminate()        


class TEMPWIDGET(QWidget):
    
    def __init__(self, mte=None,parent=None):
        super().__init__()
        # super(TEMPWIDGET, self).__init__(parent)
        self.mte=mte
        self.isWinOpen=False
        self.parent=parent
        self.setup()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def setup(self) :   
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('Temperature')
        self.vbox=QVBoxLayout()
        labelT=QLabel('Temperature')
        self.tempVal= QDoubleSpinBox(self)
        self.tempVal.setSuffix(" %s" % '°C')
        self.tempVal.setMaximum(21)
        self.tempVal.setMinimum(-40)
        self.tempVal.setValue(20)
        self.tempSet=QPushButton('Set')
        self.hbox=QHBoxLayout()
        self.hbox.addWidget(labelT)
        self.hbox.addWidget(self.tempVal)
        self.hbox.addWidget(self.tempSet)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)
        self.tempSet.clicked.connect(self.SET)
        
    def SET(self):
        temp = self.tempVal.value()
        self.mte.SetTemperature(temp)
        # self.mte.sendConfiguration()
    
    def closeEvent(self, event):
        """ when closing the window
        """
        self.isWinOpen=False
        
        time.sleep(0.1)
        event.accept() 
        
        
class SETTINGWIDGET(QWidget):
    
    def __init__(self, mte=None,visualisation=None,parent=None):
        
        super(SETTINGWIDGET, self).__init__(parent)
        self.mte=mte
        self.visualisation=visualisation
        self.isWinOpen=False
        self.parent=parent
        self.setup()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        
        self.actionButton()
        self.roi1Is=False
        
    def setup(self) : 
        self.dimx = self.mte.getParameter("PicamParameter_ActiveWidth")
        self.dimy = self.mte.getParameter("PicamParameter_ActiveHeight")
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('SETTINGS')
        self.vbox=QVBoxLayout()
        
        hboxShutter=QHBoxLayout()
        shutterLabel=QLabel('ShutterMode')
        self.shutterMode=QComboBox()
        self.shutterMode.setMaximumWidth(100)
        self.shutterMode.addItem('Normal')
        self.shutterMode.addItem('Always Close')
        self.shutterMode.addItem('Always Open')
        self.shutterMode.addItem('Open before trig')
        
        hboxShutter.addWidget(shutterLabel)
        hboxShutter.addWidget(self.shutterMode)
        self.vbox.addLayout(hboxShutter)
        
        hboxFrequency=QHBoxLayout()
        frequencyLabel=QLabel('Frequency')
        self.frequency=QComboBox()
        self.frequency.setMaximumWidth(100)
        self.frequency.addItem('Normal')
        self.frequency.addItem('Always Close')
        self.frequency.addItem('Always Open')
        hboxFrequency.addWidget(frequencyLabel)
        hboxFrequency.addWidget(self.frequency)
        self.vbox.addLayout(hboxFrequency)
        
        hboxROI=QHBoxLayout()
        
        hbuttonROI=QVBoxLayout()
        self.setROIButton=QPushButton('Set ROI')
        self.setROIFullButton=QPushButton('Set full Frame')
        self.setROIMouseButton=QPushButton('Mousse')
        hbuttonROI.addWidget(self.setROIButton)
        hbuttonROI.addWidget(self.setROIFullButton)
        hbuttonROI.addWidget(self.setROIMouseButton)
        hboxROI.addLayout(hbuttonROI)
        
        roiLay= QVBoxLayout()
        labelROIX=QLabel('ROI Xo')
        self.ROIX=QDoubleSpinBox(self)
        self.ROIX.setMinimum(0)
        self.ROIX.setMaximum(self.dimx)
        
        self.ROIY=QDoubleSpinBox(self)
        self.ROIY.setMinimum(1)
        self.ROIY.setMaximum(self.dimy)
        labelROIY=QLabel('ROI Yo')
        
        labelROIW=QLabel('ROI Width')
        self.ROIW=QDoubleSpinBox(self)
        self.ROIW.setMinimum(0)
        self.ROIW.setMaximum(self.dimx)     
        
        labelROIH=QLabel('ROI Height')
        self.ROIH=QDoubleSpinBox(self)
        self.ROIH.setMinimum(1)
        self.ROIH.setMaximum(self.dimy) 
        
        labelBinX=QLabel('Bin X')
        self.BINX=QDoubleSpinBox(self)
        self.BINX.setMinimum(1)
        self.BINX.setMaximum(self.dimx) 
        labelBinY=QLabel('Bin Y ')
        self.BINY=QDoubleSpinBox(self)
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
        
        self.r1=100
        self.roi1=pg.RectROI([self.dimx/2,self.dimy/2], [2*self.r1, 2*self.r1],pen='r',movable=True)
        self.roi1.setPos([self.dimx/2-self.r1,self.dimy/2-self.r1])
        
    def actionButton(self):
        self.setROIButton.clicked.connect(self.roiSet)
        self.setROIFullButton.clicked.connect(self.roiFull)
        self.frequency.currentIndexChanged.connect(self.setFrequency)
        self.shutterMode.currentIndexChanged.connect(self.setShutterMode)
        self.setROIMouseButton.clicked.connect(self.mousseROI)
        self.roi1.sigRegionChangeFinished.connect(self.moussFinished)
        
    def mousseROI(self):
        
        self.visualisation.p1.addItem(self.roi1)
        self.roi1Is=True
        
    def moussFinished(self):
        
        posRoi=self.roi1.pos()
        sizeRoi=self.roi1.size()
        self.x0=int(posRoi.x())
        self.wroi=int(sizeRoi.x())
        self.hroi=int(sizeRoi.y())
        self.y0=posRoi.y()+sizeRoi.y()
        
        self.ROIX.setValue(self.x0)
        self.ROIY.setValue(self.y0)
        self.ROIW.setValue(self.wroi)
        self.ROIH.setValue(self.hroi)
        
    def roiSet(self):
        
        self.x0=int(self.ROIX.value())
        self.y0=int(self.ROIY.value())
        self.w=int(self.ROIW.value())
        self.h=int(self.ROIH.value())
        self.BinX=int(self.BINX.value())
        self.binY=int(self.BINY.value())
        
        self.mte.setROI(self.x0, self.w, self.binX, self.y0, self.h, self.binY, 1)
        self.mte.sendConfiguration()
        
        if self.roi1Is==True:
            self.visualisation.p1.removeItem(self.roi1)
            self.roi1Is=False
        
    def roiFull(self):
        
        self.w = self.mte.getParameter("PicamParameter_ActiveWidth")
        self.h = self.mte.getParameter("PicamParameter_ActiveHeight")
#        self.ROIX.setValue(0)
#        self.ROIY.setValue(0)
#        self.ROIW.setValue(self.w)
#        self.ROIH.setValue(self.h)
        self.mte.setROI(0, self.w, 1, 0, self.h, 1, 0) # full frame
        self.mte.sendConfiguration()
        print("fullframe")
        if self.roi1Is==True:
            self.visualisation.p1.removeItem(self.roi1)
            self.roi1Is=False
        
    def setFrequency(self) :
        """
        set frequency reading in Mhz
        """          
        ifreq=self.freqency.currentIndex()
        if ifreq==0:
             self.mte.setParameter("PicamParameter_AdcSpeed",0.1)
        if ifreq==0:
             self.mte.setParameter("PicamParameter_AdcSpeed",1)
        if ifreq==0:
             self.mte.setParameter("PicamParameter_AdcSpeed",2)
             
        print('adc frequency(Mhz)',self.mte.getParameter("AdcSpeed"))

    def setShutterMode(self):
        """ set shutter mode
        """
        ishut=self.shutterMode.currentIndex()
        print('shutter')
        if ishut==0:
             self.mte.setParameter("PicamParameter_ShutterTimingMode",0)
        if ishut==1:
             self.mte.setParameter("PicamParameter_ShutterTimingMode",1) 
        if ishut==2:
             self.mte.setParameter("PicamParameter_ShutterTimingMode",2) 
        if ishut==3:
             self.mte.setParameter("PicamParameter_ShutterTimingMode",3)
             print('OutputSignal',self.mte.getParameter("ShutterTimingMode"))
             
    def closeEvent(self, event):
        """ when closing the window
        """
        self.isWinOpen=False
        if self.roi1Is==True:
            self.visualisation.p1.removeItem(self.roi1)
            self.roi1Is=False
        time.sleep(0.1)
        
        event.accept() 
        
if __name__ == "__main__":       
    
    appli = QApplication(sys.argv)
    confpathVisu='C:/Users/GAUTIER/Desktop/python/princeton/confCCD.ini'
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    e = ROPPER(cam='cam0',confpath=confpathVisu)  
    e.show()
    appli.exec_()       